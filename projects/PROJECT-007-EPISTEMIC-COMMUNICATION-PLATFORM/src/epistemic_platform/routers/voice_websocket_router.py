"""Voice WebSocket router — /ws/voice/{session_id} bidirectional audio endpoint.

Handles real-time voice conversation over WebSocket with interleaved
binary audio frames and JSON control messages. Supports barge-in
(client can interrupt TTS playback) and per-turn latency monitoring.
"""

from __future__ import annotations

import asyncio
import enum
import json
import logging
import re
import statistics
import time
from dataclasses import dataclass, field

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from epistemic_platform.config import get_settings
from epistemic_platform.database import async_session_factory
from epistemic_platform.engine.achievement_engine import AchievementEngine
from epistemic_platform.engine.conversation_manager import ConversationManager
from epistemic_platform.engine.history_context import build_history_context
from epistemic_platform.llm.claude_adapter import ClaudeConversationAdapter, ClaudeCoachingAdapter
from epistemic_platform.ontology.expressive_state import ExpressiveState
from epistemic_platform.repositories.actor_profile_repository import ActorProfileRepository
from epistemic_platform.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)
from epistemic_platform.repositories.user_profile_repository import UserProfileRepository
from epistemic_platform.voice.elevenlabs_tts import ElevenLabsTTSClient
from epistemic_platform.voice.whisper_stt import WhisperSTTClient
from epistemic_platform.voice.voice_analyser import VoiceAnalyser

logger = logging.getLogger(__name__)

router = APIRouter()

_META_RE = re.compile(r"\|\|\|META\|\|\|(\{.*\})\s*$", re.DOTALL)
_META_SENTINEL = "|||META|||"

# End-session detection
_END_SESSION_TOKEN = "[END_SESSION]"
_FAREWELL_RE = re.compile(
    r"\b(goodbye|good bye|bye bye|bye for now|see you later|see you soon"
    r"|thanks bye|that'?s all|end session|i'?m done|gotta go|take care"
    r"|until next time|cheers|farewell|nice talking|talk later)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# State machine & metrics
# ---------------------------------------------------------------------------


class VoiceState(enum.Enum):
    """Server-side voice pipeline state."""

    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


@dataclass
class TurnLatency:
    """Latency breakdown for a single conversation turn."""

    stt_ms: float = 0.0
    llm_ms: float = 0.0
    tts_first_byte_ms: float = 0.0
    total_ms: float = 0.0


@dataclass
class SessionMetrics:
    """Accumulated metrics across a voice session."""

    turn_latencies: list[TurnLatency] = field(default_factory=list)
    barge_in_count: int = 0

    def summary(self) -> dict:
        """Return aggregate latency stats and barge-in count."""
        totals = [t.total_ms for t in self.turn_latencies]
        result: dict = {"barge_in_count": self.barge_in_count}
        if not totals:
            return result
        result.update(
            {
                "turn_count": len(totals),
                "latency_avg_ms": round(statistics.mean(totals)),
                "latency_p50_ms": round(statistics.median(totals)),
                "latency_p90_ms": round(_percentile(totals, 90)),
                "latency_max_ms": round(max(totals)),
            }
        )
        return result


def _percentile(data: list[float], p: float) -> float:
    """Simple percentile without numpy."""
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (k - f) * (s[c] - s[f])


async def _cancel_tts(task: asyncio.Task, timeout: float = 0.5) -> None:
    """Cancel a running TTS task with a brief grace period."""
    task.cancel()
    try:
        await asyncio.wait_for(asyncio.shield(task), timeout=timeout)
    except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
        pass


def _authenticate_ws(token: str | None) -> int | None:
    """Validate JWT from query param. Returns user_id or None."""
    if not token:
        logger.warning("Voice WS: no token provided")
        return None
    from epistemic_platform.auth import decode_token

    payload = decode_token(token)
    if payload is None:
        logger.warning("Voice WS: token decode failed")
        return None
    if payload.get("type") != "access":
        logger.warning("Voice WS: token type=%s (expected access)", payload.get("type"))
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
    first_byte_event: asyncio.Event | None = None,
) -> None:
    """Stream TTS audio chunks to the client. Stops when cancel is set.

    If *first_byte_event* is provided it is set after the first audio
    chunk is sent, allowing callers to measure time-to-first-byte.
    """
    try:
        async for chunk in tts.synthesize_stream(text, voice_params):
            if cancel.is_set():
                break
            await websocket.send_bytes(chunk)
            if first_byte_event and not first_byte_event.is_set():
                first_byte_event.set()
    except asyncio.CancelledError:
        logger.debug("TTS streaming cancelled (barge-in)")
    except Exception:
        logger.exception("TTS streaming error")
    finally:
        # Unblock any waiters even on error / cancel
        if first_byte_event and not first_byte_event.is_set():
            first_byte_event.set()
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
        {"type": "ping"}: connection health check

    Server -> Client:
        {"type": "transcription", "text": "..."}
        {"type": "stream_start"} / {"type": "stream_delta", "content": "..."} / {"type": "stream_end"}
        Binary frames: TTS audio chunks (MP3)
        {"type": "audio_end"}
        {"type": "vocal_state", "composure_score": ..., ...}
        {"type": "trilemma_update", ...} / {"type": "stance_update", ...}
        {"type": "coaching", "annotation": {...}}
        {"type": "state_change", "state": "listening|processing|speaking"}
        {"type": "barge_in"}
        {"type": "latency_report", "turn": N, "stt_ms": ..., ...}
        {"type": "pong", "server_ts": ...}
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
    analyser = VoiceAnalyser()
    vocal_states: list[dict] = []
    tts: ElevenLabsTTSClient | None = None
    tts_task: asyncio.Task | None = None
    barge_in = asyncio.Event()

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

            user_repo = UserProfileRepository(db)
            user = await user_repo.get(user_id)
            if not user:
                await websocket.send_json(
                    {"type": "error", "detail": "User not found"}
                )
                return

            # Per-actor voice: prefer actor's voice_id, fall back to global default
            voice_id = (actor.ontology_config or {}).get("voice_id") or settings.elevenlabs_default_voice_id
            tts = ElevenLabsTTSClient(
                api_key=settings.elevenlabs_api_key,
                voice_id=voice_id,
                model_id=settings.elevenlabs_model_id,
            )

            # Build cross-session history context
            prior_sessions = await session_repo.list_recent_completed_by_user(
                user_id, exclude_session_id=session_id, limit=10,
            )
            prefs = (user.preferences or {}) if user else {}
            history = build_history_context(
                sessions=prior_sessions,
                current_actor_id=session.actor_id,
                proficiency=prefs.get("proficiency"),
            )

            conv_manager = ConversationManager(
                session=session,
                actor=actor,
                conversation_llm=ClaudeConversationAdapter(),
                coaching_llm=ClaudeCoachingAdapter(),
                db=db,
                history=history,
            )

            audio_buffer = bytearray()
            tts_task: asyncio.Task | None = None
            post_task: asyncio.Task | None = None
            barge_in = asyncio.Event()
            tts_first_byte = asyncio.Event()
            latency_warn_ms = settings.voice_latency_warn_threshold_ms
            cancel_timeout = settings.voice_barge_in_cancel_timeout_ms / 1000.0
            metrics = SessionMetrics()
            state = VoiceState.LISTENING

            await websocket.send_json(
                {"type": "state_change", "state": state.value}
            )

            while True:
                message = await websocket.receive()

                if message.get("type") == "websocket.disconnect":
                    break

                # --- Binary frame: audio chunk ---
                raw_bytes = message.get("bytes")
                if raw_bytes:
                    if tts_task and not tts_task.done():
                        # Barge-in: cancel TTS immediately
                        barge_in.set()
                        await _cancel_tts(tts_task, timeout=cancel_timeout)
                        tts_task = None
                        metrics.barge_in_count += 1
                        state = VoiceState.LISTENING
                        await websocket.send_json({"type": "barge_in"})
                        await websocket.send_json(
                            {"type": "state_change", "state": state.value}
                        )
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
                        await _cancel_tts(tts_task, timeout=cancel_timeout)

                    # Wait for background post-processing to finish
                    # so coaching/horn/stance data is persisted before scoring
                    if post_task and not post_task.done():
                        try:
                            await asyncio.wait_for(post_task, timeout=15.0)
                        except asyncio.TimeoutError:
                            logger.warning(
                                "Post-processing timed out before end_session session=%d",
                                session_id,
                            )
                        except Exception:
                            logger.exception(
                                "Post-processing error before end_session session=%d",
                                session_id,
                            )

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

                    # Merge composure + session-level latency / barge-in stats
                    extra = {**metrics.summary()}
                    if composure_metrics:
                        extra.update(composure_metrics)

                    outcome = await conv_manager.end_session(
                        extra_metrics=extra if extra else None
                    )

                    # Run achievement engine to compute scores, XP, proficiency
                    reward_data = None
                    try:
                        engine = AchievementEngine(db)
                        reward = await engine.process_session(session, user)
                        session.trilemma_state = {
                            **(session.trilemma_state or {}),
                            "reward_processed": True,
                        }
                        await db.commit()
                        reward_data = reward.to_dict()
                        logger.info(
                            "Voice session %d reward: grade=%s xp=+%d",
                            session_id,
                            reward.score.grade if reward.score else "?",
                            reward.xp_award.total if reward.xp_award else 0,
                        )
                    except Exception:
                        logger.exception(
                            "AchievementEngine failed for session %d", session_id
                        )

                    msg: dict = {"type": "session_ended", "outcome": outcome}
                    if reward_data:
                        msg["reward"] = reward_data
                    await websocket.send_json(msg)
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
                        await _cancel_tts(tts_task, timeout=cancel_timeout)
                        tts_task = None
                        metrics.barge_in_count += 1

                    state = VoiceState.PROCESSING
                    await websocket.send_json(
                        {"type": "state_change", "state": state.value}
                    )

                    t0 = time.monotonic()
                    audio_data = bytes(audio_buffer)
                    audio_buffer.clear()
                    barge_in.clear()

                    # --- STT (required) + composure analysis (optional, best-effort) ---
                    if len(audio_data) < 1000:
                        logger.warning("Audio too short (%d bytes) session=%d, skipping", len(audio_data), session_id)
                        state = VoiceState.LISTENING
                        await websocket.send_json(
                            {"type": "state_change", "state": state.value}
                        )
                        continue

                    # Run STT and voice analysis in PARALLEL (analysis is non-blocking)
                    analyse_task = asyncio.create_task(analyser.analyse(audio_data))

                    try:
                        transcription = await stt.transcribe(audio_data, audio_format="webm")
                    except Exception as stt_err:
                        logger.exception("STT failed session=%d", session_id)
                        analyse_task.cancel()
                        state = VoiceState.LISTENING
                        await websocket.send_json(
                            {"type": "state_change", "state": state.value}
                        )
                        detail = "Speech service unavailable"
                        if "insufficient_quota" in str(stt_err) or "429" in str(stt_err):
                            detail = "Speech service quota exceeded — please check OpenAI billing"
                        await websocket.send_json(
                            {"type": "error", "detail": detail}
                        )
                        continue
                    t_stt = time.monotonic()

                    # Collect voice analysis result (should be done by now or nearly)
                    try:
                        vocal_state = await asyncio.wait_for(analyse_task, timeout=2.0)
                    except (asyncio.TimeoutError, Exception):
                        logger.debug("Voice analysis skipped/timed-out session=%d", session_id)
                        vocal_state = None

                    if not transcription.text:
                        state = VoiceState.LISTENING
                        await websocket.send_json(
                            {"type": "state_change", "state": state.value}
                        )
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

                    # Check for user farewell phrases
                    user_farewell = bool(_FAREWELL_RE.search(transcription.text))

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
                    _pending = ""
                    _meta_found = False
                    async for chunk in conv_manager.stream_response(
                        transcription.text,
                        user_vocal_state=vocal_dict,
                    ):
                        if chunk.delta:
                            raw_response += chunk.delta
                            if _meta_found:
                                continue
                            _pending += chunk.delta
                            _mi = _pending.find(_META_SENTINEL)
                            if _mi >= 0:
                                if _mi > 0:
                                    clean_delta = _pending[:_mi].replace(_END_SESSION_TOKEN, "")
                                    if clean_delta:
                                        await websocket.send_json(
                                            {"type": "stream_delta", "content": clean_delta}
                                        )
                                _pending = ""
                                _meta_found = True
                                continue
                            _flush = len(_pending)
                            for _i in range(1, min(len(_META_SENTINEL), len(_pending)) + 1):
                                if _META_SENTINEL.startswith(_pending[-_i:]):
                                    _flush = len(_pending) - _i
                                    break
                            if _flush > 0:
                                _delta_text = _pending[:_flush].replace(_END_SESSION_TOKEN, "")
                                if _delta_text:
                                    await websocket.send_json(
                                        {"type": "stream_delta", "content": _delta_text}
                                    )
                                _pending = _pending[_flush:]

                    if _pending and not _meta_found:
                        _final_text = _pending.replace(_END_SESSION_TOKEN, "")
                        if _final_text:
                            await websocket.send_json(
                                {"type": "stream_delta", "content": _final_text}
                            )

                    await websocket.send_json({"type": "stream_end"})
                    t_llm = time.monotonic()

                    # Parse ExpressiveState for TTS voice params
                    clean_text, expressive_state = _strip_meta(raw_response)

                    # Check for actor-initiated end (LLM includes [END_SESSION])
                    actor_farewell = _END_SESSION_TOKEN in clean_text
                    if actor_farewell:
                        clean_text = clean_text.replace(_END_SESSION_TOKEN, "").strip()

                    # Determine if session should end after this turn
                    should_end_session = user_farewell or actor_farewell

                    # --- Start TTS IMMEDIATELY (don't wait for horn/stance/coaching) ---
                    tts_first_byte_ms = 0.0
                    use_heygen = (
                        settings.avatar_mode == "heygen"
                        and settings.heygen_api_key
                        and (actor.avatar_config or {}).get("heygen_avatar_id")
                    )
                    if clean_text.strip():
                        if use_heygen:
                            # HeyGen mode: send text to frontend, which forwards to HeyGen API
                            # HeyGen does its own TTS + facial animation via LiveKit
                            mood = (
                                expressive_state.mood
                                if expressive_state and expressive_state.mood
                                else None
                            )
                            await websocket.send_json(
                                {
                                    "type": "heygen_speak",
                                    "text": clean_text,
                                    **({"mood": mood} if mood else {}),
                                }
                            )
                            state = VoiceState.SPEAKING
                            await websocket.send_json(
                                {"type": "state_change", "state": state.value}
                            )
                        else:
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
                            tts_first_byte.clear()
                            t_tts_start = time.monotonic()
                            tts_task = asyncio.create_task(
                                _stream_tts(
                                    websocket,
                                    tts,
                                    clean_text,
                                    voice_params,
                                    barge_in,
                                    first_byte_event=tts_first_byte,
                                )
                            )
                            state = VoiceState.SPEAKING
                            await websocket.send_json(
                                {"type": "state_change", "state": state.value}
                            )

                            # Wait briefly for first TTS byte (non-blocking cap)
                            try:
                                await asyncio.wait_for(
                                    tts_first_byte.wait(), timeout=5.0
                                )
                                tts_first_byte_ms = (
                                    time.monotonic() - t_tts_start
                                ) * 1000
                            except asyncio.TimeoutError:
                                tts_first_byte_ms = 5000.0

                    # --- Post-processing in background (horn/stance/coaching/DB) ---
                    # This runs while TTS is streaming, so user hears the
                    # response without waiting for analysis.
                    async def _background_post_process():
                        try:
                            await conv_manager.post_process_turn(raw_response)

                            horn = conv_manager.get_last_horn_detection()
                            if horn:
                                try:
                                    await websocket.send_json(
                                        {
                                            "type": "trilemma_update",
                                            "state": conv_manager.get_trilemma_state(),
                                            "horn_detection": horn,
                                        }
                                    )
                                except Exception:
                                    pass  # WS may be closed

                            stance = conv_manager.get_last_stance_detection()
                            if stance:
                                try:
                                    await websocket.send_json(
                                        {"type": "stance_update", "detection": stance}
                                    )
                                except Exception:
                                    pass

                            annotation = await conv_manager.maybe_run_coaching()
                            if annotation:
                                try:
                                    await websocket.send_json(
                                        {"type": "coaching", "annotation": annotation.to_dict()}
                                    )
                                except Exception:
                                    pass
                        except Exception:
                            logger.exception(
                                "Background post-processing failed session=%d",
                                session_id,
                            )

                    post_task = asyncio.create_task(_background_post_process())

                    # Latency logging + client report
                    t_end = time.monotonic()
                    stt_ms = (t_stt - t0) * 1000
                    llm_ms = (t_llm - t_stt) * 1000
                    total_ms = (t_end - t0) * 1000

                    turn_lat = TurnLatency(
                        stt_ms=stt_ms,
                        llm_ms=llm_ms,
                        tts_first_byte_ms=tts_first_byte_ms,
                        total_ms=total_ms,
                    )
                    metrics.turn_latencies.append(turn_lat)

                    logger.info(
                        "Voice pipeline session=%d: STT=%.0fms LLM=%.0fms "
                        "TTS-FB=%.0fms total=%.0fms",
                        session_id,
                        stt_ms,
                        llm_ms,
                        tts_first_byte_ms,
                        total_ms,
                    )
                    if total_ms > latency_warn_ms:
                        logger.warning(
                            "Voice latency exceeded %dms (%.0fms) session=%d",
                            latency_warn_ms,
                            total_ms,
                            session_id,
                        )

                    await websocket.send_json(
                        {
                            "type": "latency_report",
                            "turn": len(metrics.turn_latencies),
                            "stt_ms": round(stt_ms),
                            "llm_ms": round(llm_ms),
                            "tts_first_byte_ms": round(tts_first_byte_ms),
                            "total_ms": round(total_ms),
                        }
                    )

                    # Auto-end session after farewell TTS plays
                    if should_end_session:
                        logger.info(
                            "Auto-ending session %d (user_farewell=%s, actor_farewell=%s)",
                            session_id, user_farewell, actor_farewell,
                        )
                        # Wait for TTS to finish playing before ending
                        if tts_task and not tts_task.done():
                            try:
                                await asyncio.wait_for(tts_task, timeout=30.0)
                            except (asyncio.TimeoutError, asyncio.CancelledError):
                                pass
                        # Wait for post-processing
                        if post_task and not post_task.done():
                            try:
                                await asyncio.wait_for(post_task, timeout=15.0)
                            except (asyncio.TimeoutError, Exception):
                                pass

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

                        extra = {**metrics.summary()}
                        if composure_metrics:
                            extra.update(composure_metrics)

                        outcome = await conv_manager.end_session(
                            extra_metrics=extra if extra else None
                        )

                        reward_data = None
                        try:
                            engine = AchievementEngine(db)
                            reward = await engine.process_session(session, user)
                            session.trilemma_state = {
                                **(session.trilemma_state or {}),
                                "reward_processed": True,
                            }
                            await db.commit()
                            reward_data = reward.to_dict()
                        except Exception:
                            logger.exception(
                                "AchievementEngine failed for session %d", session_id
                            )

                        end_msg: dict = {"type": "session_ended", "outcome": outcome}
                        if reward_data:
                            end_msg["reward"] = reward_data
                        await websocket.send_json(end_msg)
                        break

                    continue

                # ---- ping (connection health check) ----
                if cmd == "ping":
                    client_ts = msg.get("ts")
                    await websocket.send_json(
                        {
                            "type": "pong",
                            "server_ts": time.time(),
                            **({"client_ts": client_ts} if client_ts else {}),
                        }
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
        # Let post-processing finish so scores/coaching persist to DB
        if post_task and not post_task.done():
            try:
                await asyncio.wait_for(post_task, timeout=10.0)
            except (asyncio.TimeoutError, asyncio.CancelledError, Exception):
                logger.warning(
                    "Post-processing did not complete on disconnect session=%d",
                    session_id,
                )
        if tts:
            await tts.close()
        await stt.close()
