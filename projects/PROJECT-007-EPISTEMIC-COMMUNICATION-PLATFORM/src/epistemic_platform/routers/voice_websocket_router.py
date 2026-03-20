"""Voice WebSocket router — /ws/voice/{session_id} bidirectional audio endpoint.

Handles real-time voice conversation over WebSocket with interleaved
binary audio frames and JSON control messages. Supports barge-in
(client can interrupt TTS playback) and per-turn latency monitoring.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from epistemic_platform.config import get_settings
from epistemic_platform.database import async_session_factory
from epistemic_platform.engine.conversation_manager import ConversationManager
from epistemic_platform.llm.claude_adapter import ClaudeConversationAdapter, ClaudeCoachingAdapter
from epistemic_platform.ontology.expressive_state import ExpressiveState
from epistemic_platform.repositories.actor_profile_repository import ActorProfileRepository
from epistemic_platform.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)
from epistemic_platform.voice.elevenlabs_tts import ElevenLabsTTSClient
from epistemic_platform.voice.whisper_stt import WhisperSTTClient
from epistemic_platform.voice.voice_analyser import VoiceAnalyser

logger = logging.getLogger(__name__)

router = APIRouter()

_META_RE = re.compile(r"\|\|\|META\|\|\|(\{.*\})\s*$", re.DOTALL)


def _authenticate_ws(token: str | None) -> int | None:
    """Validate JWT from query param. Returns user_id or None."""
    if not token:
        return None
    from epistemic_platform.auth import decode_token

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None
    return int(payload["sub"])


def _strip_meta(text: str) -> tuple[str, ExpressiveState | None]:
    """Strip |||META|||{...} from LLM response, parse into ExpressiveState."""
    match = _META_RE.search(text)
    if not match:
        return text.strip(), None
    clean = text[: match.start()].strip()
    try:
        meta = json.loads(match.group(1))
        return clean, ExpressiveState.from_llm_metadata(meta)
    except (json.JSONDecodeError, KeyError, ValueError):
        return clean, None


async def _stream_tts(
    websocket: WebSocket,
    tts: ElevenLabsTTSClient,
    text: str,
    voice_params: dict,
    cancel: asyncio.Event,
) -> None:
    """Stream TTS audio chunks to the client. Stops when cancel is set."""
    try:
        async for chunk in tts.synthesize_stream(text, voice_params):
            if cancel.is_set():
                break
            await websocket.send_bytes(chunk)
    except Exception:
        logger.exception("TTS streaming error")
    finally:
        try:
            await websocket.send_json({"type": "audio_end"})
        except Exception:
            pass


@router.websocket("/ws/voice/{session_id}")
async def voice_websocket(
    websocket: WebSocket,
    session_id: int,
    token: str | None = None,
):
    """Bidirectional voice conversation over WebSocket.

    Client -> Server:
        Binary frames: audio chunks (WebM/Opus from MediaRecorder)
        {"type": "end_utterance"}: signals end of user speech
        {"type": "end_session"}: ends conversation

    Server -> Client:
        {"type": "transcription", "text": "..."}
        {"type": "stream_start"} / {"type": "stream_delta", "content": "..."} / {"type": "stream_end"}
        Binary frames: TTS audio chunks (MP3)
        {"type": "audio_end"}
        {"type": "vocal_state", "composure_score": ..., ...}
        {"type": "trilemma_update", ...} / {"type": "stance_update", ...}
        {"type": "coaching", "annotation": {...}}
        {"type": "barge_in"}
        {"type": "session_ended", "outcome": {...}}
        {"type": "error", "detail": "..."}
    """
    settings = get_settings()

    # Authenticate
    user_id = _authenticate_ws(token)
    if user_id is None:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token"
        )
        return

    await websocket.accept()

    # Voice API clients
    stt = WhisperSTTClient(api_key=settings.openai_api_key, model=settings.whisper_model)
    tts = ElevenLabsTTSClient(
        api_key=settings.elevenlabs_api_key,
        voice_id=settings.elevenlabs_default_voice_id,
        model_id=settings.elevenlabs_model_id,
    )
    analyser = VoiceAnalyser()
    vocal_states: list[dict] = []

    try:
        async with async_session_factory() as db:
            # Load session + actor
            session_repo = ConversationSessionRepository(db)
            session = await session_repo.get(session_id)

            if not session or session.user_id != user_id:
                detail = "Session not found" if not session else "Not your session"
                await websocket.send_json({"type": "error", "detail": detail})
                return

            if session.status != "active":
                await websocket.send_json(
                    {"type": "error", "detail": "Session not active"}
                )
                return

            actor_repo = ActorProfileRepository(db)
            actor = await actor_repo.get(session.actor_id)
            if not actor:
                await websocket.send_json(
                    {"type": "error", "detail": "Actor not found"}
                )
                return

            conv_manager = ConversationManager(
                session=session,
                actor=actor,
                conversation_llm=ClaudeConversationAdapter(),
                coaching_llm=ClaudeCoachingAdapter(),
                db=db,
            )

            audio_buffer = bytearray()
            tts_task: asyncio.Task | None = None
            barge_in = asyncio.Event()
            latency_warn_ms = settings.voice_latency_warn_threshold_ms

            while True:
                message = await websocket.receive()

                if message.get("type") == "websocket.disconnect":
                    break

                # --- Binary frame: audio chunk ---
                raw_bytes = message.get("bytes")
                if raw_bytes:
                    if tts_task and not tts_task.done():
                        # Barge-in: cancel TTS playback
                        barge_in.set()
                        await tts_task
                        tts_task = None
                        await websocket.send_json({"type": "barge_in"})
                    audio_buffer.extend(raw_bytes)
                    continue

                # --- Text frame: JSON control ---
                raw_text = message.get("text")
                if not raw_text:
                    continue

                try:
                    msg = json.loads(raw_text)
                except json.JSONDecodeError:
                    await websocket.send_json(
                        {"type": "error", "detail": "Invalid JSON"}
                    )
                    continue

                cmd = msg.get("type")

                # ---- end_session ----
                if cmd == "end_session":
                    if tts_task and not tts_task.done():
                        barge_in.set()
                        await tts_task

                    # Aggregate composure metrics
                    composure_metrics = None
                    if vocal_states:
                        scores = [v["composure_score"] for v in vocal_states]
                        composure_metrics = {
                            "avg_composure": round(sum(scores) / len(scores), 4),
                            "min_composure": round(min(scores), 4),
                            "max_composure": round(max(scores), 4),
                            "turn_count_voice": len(scores),
                        }
                        if len(scores) >= 2:
                            composure_metrics["composure_trend"] = round(
                                scores[-1] - scores[0], 4
                            )

                    outcome = await conv_manager.end_session(
                        extra_metrics=composure_metrics
                    )
                    await websocket.send_json(
                        {"type": "session_ended", "outcome": outcome}
                    )
                    break

                # ---- end_utterance ----
                if cmd == "end_utterance":
                    if not audio_buffer:
                        await websocket.send_json(
                            {"type": "error", "detail": "No audio received"}
                        )
                        continue

                    # Cancel any lingering TTS
                    if tts_task and not tts_task.done():
                        barge_in.set()
                        await tts_task
                        tts_task = None

                    t0 = time.monotonic()
                    audio_data = bytes(audio_buffer)
                    audio_buffer.clear()
                    barge_in.clear()

                    # --- Parallel: STT + composure analysis ---
                    transcription, vocal_state = await asyncio.gather(
                        stt.transcribe(audio_data, audio_format="webm"),
                        analyser.analyse(audio_data),
                    )
                    t_stt = time.monotonic()

                    if not transcription.text:
                        await websocket.send_json(
                            {"type": "error", "detail": "Could not transcribe audio"}
                        )
                        continue

                    # Enrich vocal state with speaking rate from STT
                    if (
                        vocal_state
                        and transcription.duration
                        and transcription.duration > 0
                    ):
                        wc = len(transcription.text.split())
                        vocal_state.speaking_rate_wpm = round(
                            (wc / transcription.duration) * 60.0, 1
                        )
                        # Recompute composure with rate info
                        rd = abs(vocal_state.speaking_rate_wpm - 140.0) / 140.0
                        rs = max(0.0, 1.0 - rd)
                        ps = max(0.0, 1.0 - vocal_state.pitch_variability * 2.0)
                        js = max(0.0, 1.0 - vocal_state.jitter * 10.0)
                        vocal_state.composure_score = round(
                            min(
                                1.0,
                                max(
                                    0.0,
                                    0.35 * ps
                                    + 0.25 * js
                                    + 0.25 * vocal_state.volume_stability
                                    + 0.15 * rs,
                                ),
                            ),
                            4,
                        )

                    # Push transcription
                    await websocket.send_json(
                        {"type": "transcription", "text": transcription.text}
                    )

                    # Push vocal state
                    vocal_dict = None
                    if vocal_state:
                        vocal_dict = vocal_state.to_dict()
                        vocal_states.append(vocal_dict)
                        await websocket.send_json(
                            {"type": "vocal_state", **vocal_dict}
                        )

                    # --- Actor response via conversation engine ---
                    await websocket.send_json({"type": "stream_start"})

                    raw_response = ""
                    async for chunk in conv_manager.handle_user_message(
                        transcription.text,
                        user_vocal_state=vocal_dict,
                    ):
                        if chunk.delta:
                            raw_response += chunk.delta
                            await websocket.send_json(
                                {"type": "stream_delta", "content": chunk.delta}
                            )

                    await websocket.send_json({"type": "stream_end"})
                    t_llm = time.monotonic()

                    # Parse ExpressiveState for TTS voice params
                    clean_text, expressive_state = _strip_meta(raw_response)

                    # Push trilemma / stance / coaching
                    horn = conv_manager.get_last_horn_detection()
                    if horn:
                        await websocket.send_json(
                            {
                                "type": "trilemma_update",
                                "state": conv_manager.get_trilemma_state(),
                                "horn_detection": horn,
                            }
                        )

                    stance = conv_manager.get_last_stance_detection()
                    if stance:
                        await websocket.send_json(
                            {"type": "stance_update", "detection": stance}
                        )

                    annotation = await conv_manager.maybe_run_coaching()
                    if annotation:
                        await websocket.send_json(
                            {"type": "coaching", "annotation": annotation.to_dict()}
                        )

                    # --- Stream TTS audio (background for barge-in) ---
                    if clean_text.strip():
                        voice_params = (
                            expressive_state.to_voice_params()
                            if expressive_state
                            else {
                                "stability": 0.5,
                                "similarity_boost": 0.75,
                                "style": 0.0,
                            }
                        )
                        barge_in.clear()
                        tts_task = asyncio.create_task(
                            _stream_tts(
                                websocket, tts, clean_text, voice_params, barge_in
                            )
                        )

                    # Latency logging
                    t_end = time.monotonic()
                    stt_ms = (t_stt - t0) * 1000
                    llm_ms = (t_llm - t_stt) * 1000
                    total_ms = (t_end - t0) * 1000
                    logger.info(
                        "Voice pipeline session=%d: STT=%.0fms LLM=%.0fms total=%.0fms",
                        session_id,
                        stt_ms,
                        llm_ms,
                        total_ms,
                    )
                    if total_ms > latency_warn_ms:
                        logger.warning(
                            "Voice latency exceeded %dms (%.0fms) session=%d",
                            latency_warn_ms,
                            total_ms,
                            session_id,
                        )

                    continue

                await websocket.send_json(
                    {"type": "error", "detail": f"Unknown command: {cmd}"}
                )

    except WebSocketDisconnect:
        logger.info("Voice client disconnected: session_id=%d", session_id)
    except Exception as e:
        logger.exception("Voice WebSocket error session=%d: %s", session_id, e)
        try:
            await websocket.send_json(
                {"type": "error", "detail": "Internal server error"}
            )
        except Exception:
            pass
    finally:
        if tts_task and not tts_task.done():
            barge_in.set()
            tts_task.cancel()
        await tts.close()
        await stt.close()
