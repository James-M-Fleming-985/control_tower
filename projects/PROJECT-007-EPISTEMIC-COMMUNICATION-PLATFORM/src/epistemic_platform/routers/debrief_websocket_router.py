"""Debrief WebSocket router — /ws/debrief/{session_id} endpoint.

Handles interactive coach debrief after a conversation session completes.
Supports both text and voice modes.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, status

from epistemic_platform.auth import decode_token
from epistemic_platform.config import get_settings
from epistemic_platform.database import async_session_factory
from epistemic_platform.engine.achievement_engine import AchievementEngine, SessionReward
from epistemic_platform.engine.coach_debrief import CoachDebrief
from epistemic_platform.llm.claude_adapter import ClaudeCoachingAdapter
from epistemic_platform.models.conversation_session import ConversationSession
from epistemic_platform.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)
from epistemic_platform.repositories.user_profile_repository import UserProfileRepository

logger = logging.getLogger(__name__)

router = APIRouter()


def _authenticate_ws(token: str | None) -> int | None:
    """Validate a JWT token from query param. Returns user_id or None."""
    if not token:
        return None
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None
    return int(payload["sub"])


async def _stream_tts_debrief(
    websocket: WebSocket,
    tts: "ElevenLabsTTSClient",
    text: str,
    voice_params: dict,
) -> None:
    """Stream TTS audio for debrief coach response, then send audio_end."""
    try:
        async for chunk in tts.synthesize_stream(text, voice_params):
            await websocket.send_bytes(chunk)
    except asyncio.CancelledError:
        pass
    except Exception:
        logger.exception("Debrief TTS streaming error")
    finally:
        try:
            await websocket.send_json({"type": "audio_end"})
        except Exception:
            pass


@router.websocket("/ws/debrief/{session_id}")
async def debrief_websocket(
    websocket: WebSocket,
    session_id: int,
    token: str | None = None,
    mode: str | None = None,
):
    """WebSocket endpoint for interactive coach debrief.

    Connect: ws://host/ws/debrief/{session_id}?token=<jwt>&mode=voice

    Text mode (default):
        Client sends: {"type": "message", "content": "..."} or {"type": "end_debrief"}
        Server sends: stream_start/delta/end text

    Voice mode (mode=voice):
        Client sends: binary audio frames + {"type": "end_utterance"} or {"type": "end_debrief"}
        Server sends: stream_start/delta/end text + binary TTS audio + {"type": "audio_end"}
    """
    settings = get_settings()

    # 1. Authenticate
    user_id = _authenticate_ws(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    await websocket.accept()

    is_voice = mode == "voice"

    # Voice-specific clients
    stt = None
    tts = None
    if is_voice:
        try:
            from epistemic_platform.voice.whisper_stt import WhisperSTTClient
            from epistemic_platform.voice.elevenlabs_tts import ElevenLabsTTSClient

            stt = WhisperSTTClient(api_key=settings.openai_api_key, model=settings.whisper_model)
            coach_voice_id = settings.elevenlabs_coach_voice_id or settings.elevenlabs_default_voice_id
            if coach_voice_id and settings.elevenlabs_api_key:
                tts = ElevenLabsTTSClient(
                    api_key=settings.elevenlabs_api_key,
                    voice_id=coach_voice_id,
                    model_id=settings.elevenlabs_model_id,
                )
            else:
                logger.warning("Voice debrief: no coach voice configured, falling back to text-only")
                is_voice = False
        except Exception:
            logger.exception("Failed to initialise voice clients for debrief")
            is_voice = False

    async with async_session_factory() as db:
        # 2. Load user
        user_repo = UserProfileRepository(db)
        user = await user_repo.get(user_id)
        if not user:
            await websocket.send_json({"type": "error", "detail": "User not found"})
            await websocket.close()
            return

        # 3. Load parent session
        session_repo = ConversationSessionRepository(db)
        parent_session = await session_repo.get(session_id)

        if not parent_session:
            await websocket.send_json({"type": "error", "detail": "Session not found"})
            await websocket.close()
            return

        if parent_session.user_id != user_id:
            await websocket.send_json({"type": "error", "detail": "Not your session"})
            await websocket.close()
            return

        if parent_session.status != "completed":
            await websocket.send_json({"type": "error", "detail": "Session not completed"})
            await websocket.close()
            return

        # 4. Run achievement engine to get SessionReward
        engine = AchievementEngine(db)
        reward = await engine.process_session(parent_session, user)
        await db.commit()

        # 5. Check for existing debrief session
        existing_debrief = await session_repo.get_debrief_for_parent(session_id)
        coaching_llm = ClaudeCoachingAdapter()

        if existing_debrief and existing_debrief.status == "completed":
            # ── Replay completed debrief (read-only) ──────────────────
            await websocket.send_json({
                "type": "debrief_start",
                "session_id": existing_debrief.id,
                "mode": "voice" if is_voice else "text",
            })
            for msg in existing_debrief.messages or []:
                role = msg.get("role", "assistant")
                content = msg.get("content", "")
                await websocket.send_json({
                    "type": "debrief_replay_message",
                    "role": role,
                    "content": content,
                })
            await websocket.send_json({
                "type": "debrief_ended",
                "reward": reward.to_dict(),
                "replay": True,
            })
            try:
                await websocket.close()
            except Exception:
                pass
            return

        if existing_debrief and existing_debrief.status == "active":
            # ── Resume active debrief ─────────────────────────────────
            debrief_session = existing_debrief
            stored_messages = debrief_session.messages or []

            await websocket.send_json({
                "type": "debrief_start",
                "session_id": debrief_session.id,
                "mode": "voice" if is_voice else "text",
            })
            for msg in stored_messages:
                role = msg.get("role", "assistant")
                content = msg.get("content", "")
                await websocket.send_json({
                    "type": "debrief_replay_message",
                    "role": role,
                    "content": content,
                })

            debrief = CoachDebrief(
                coaching_llm=coaching_llm,
                reward=reward,
                parent_messages=parent_session.messages or [],
                existing_messages=stored_messages,
            )

        else:
            # ── Create new debrief session ────────────────────────────
            debrief_session = ConversationSession(
                user_id=user_id,
                actor_id=parent_session.actor_id,
                scenario_id=parent_session.scenario_id,
                parent_session_id=parent_session.id,
                status="active",
                mode="voice" if is_voice else "text",
                messages=[],
                coaching_annotations=[],
                trilemma_state={},
                turn_count=0,
                started_at=datetime.now(timezone.utc),
            )
            db.add(debrief_session)
            await db.flush()

            debrief = CoachDebrief(
                coaching_llm=coaching_llm,
                reward=reward,
                parent_messages=parent_session.messages or [],
            )

            # Send opening message
            await websocket.send_json({
                "type": "debrief_start",
                "session_id": debrief_session.id,
                "mode": "voice" if is_voice else "text",
            })
            await websocket.send_json({"type": "stream_start"})

            opening_text = ""
            async for chunk in debrief.get_opening_message():
                if chunk.delta:
                    opening_text += chunk.delta
                    await websocket.send_json({
                        "type": "stream_delta",
                        "content": chunk.delta,
                    })
            await websocket.send_json({"type": "stream_end"})

            # TTS for opening message in voice mode
            if is_voice and tts and opening_text.strip():
                await _stream_tts_debrief(
                    websocket, tts, opening_text, {"stability": 0.6, "similarity_boost": 0.75},
                )

            debrief_session.messages = [
                *debrief_session.messages,
                {"role": "assistant", "content": opening_text},
            ]
            await db.flush()

        # 6. Message loop
        audio_buffer = bytearray()
        tts_task: asyncio.Task | None = None
        voice_params = {"stability": 0.6, "similarity_boost": 0.75}

        try:
            while not debrief.is_complete:
                message = await websocket.receive()

                if message.get("type") == "websocket.disconnect":
                    break

                # --- Binary frame: audio chunk (voice mode) ---
                raw_bytes = message.get("bytes")
                if raw_bytes and is_voice:
                    # Cancel any playing TTS (barge-in)
                    if tts_task and not tts_task.done():
                        tts_task.cancel()
                        tts_task = None
                        try:
                            await websocket.send_json({"type": "barge_in"})
                        except Exception:
                            pass
                    audio_buffer.extend(raw_bytes)
                    continue

                # --- Text frame: JSON control ---
                raw_text = message.get("text")
                if not raw_text:
                    continue

                data = json.loads(raw_text)
                msg_type = data.get("type", "")

                if msg_type == "end_debrief":
                    break

                # --- Voice: end_utterance → STT → coach response ---
                if msg_type == "end_utterance" and is_voice and stt:
                    if not audio_buffer:
                        continue

                    audio_data = bytes(audio_buffer)
                    audio_buffer.clear()

                    if len(audio_data) < 1000:
                        continue

                    # Transcribe
                    try:
                        transcription = await stt.transcribe(audio_data, audio_format="webm")
                    except Exception:
                        logger.exception("Debrief STT failed session=%d", session_id)
                        await websocket.send_json({"type": "error", "detail": "Speech transcription failed"})
                        continue

                    if not transcription.text:
                        await websocket.send_json({"type": "error", "detail": "Could not transcribe audio"})
                        continue

                    # Send transcription to client
                    await websocket.send_json({"type": "transcription", "text": transcription.text})

                    content = transcription.text.strip()

                    # Store and stream coach response (same as text mode below)
                    debrief_session.messages = [
                        *debrief_session.messages,
                        {"role": "user", "content": content},
                    ]
                    debrief_session.turn_count += 1
                    await db.flush()

                    await websocket.send_json({"type": "stream_start"})
                    response_text = ""
                    async for chunk in debrief.handle_message(content):
                        if chunk.delta:
                            response_text += chunk.delta
                            await websocket.send_json({
                                "type": "stream_delta",
                                "content": chunk.delta,
                            })
                    await websocket.send_json({"type": "stream_end"})

                    # TTS for coach response
                    if tts and response_text.strip():
                        tts_task = asyncio.create_task(
                            _stream_tts_debrief(websocket, tts, response_text, voice_params)
                        )

                    debrief_session.messages = [
                        *debrief_session.messages,
                        {"role": "assistant", "content": response_text},
                    ]
                    await db.flush()
                    continue

                # --- Text: message → coach response ---
                if msg_type == "message":
                    content = data.get("content", "").strip()
                    if not content:
                        continue

                    debrief_session.messages = [
                        *debrief_session.messages,
                        {"role": "user", "content": content},
                    ]
                    debrief_session.turn_count += 1
                    await db.flush()

                    await websocket.send_json({"type": "stream_start"})
                    response_text = ""
                    async for chunk in debrief.handle_message(content):
                        if chunk.delta:
                            response_text += chunk.delta
                            await websocket.send_json({
                                "type": "stream_delta",
                                "content": chunk.delta,
                            })
                    await websocket.send_json({"type": "stream_end"})

                    # TTS for text-mode voice toggle
                    if is_voice and tts and response_text.strip():
                        tts_task = asyncio.create_task(
                            _stream_tts_debrief(websocket, tts, response_text, voice_params)
                        )

                    debrief_session.messages = [
                        *debrief_session.messages,
                        {"role": "assistant", "content": response_text},
                    ]
                    await db.flush()

        except Exception as e:
            logger.warning("Debrief WebSocket error for session %d: %s", session_id, e)

        # 7. Cleanup
        if tts_task and not tts_task.done():
            tts_task.cancel()

        debrief_session.status = "completed"
        debrief_session.ended_at = datetime.now(timezone.utc)
        await db.flush()
        await db.commit()

        await websocket.send_json({
            "type": "debrief_ended",
            "reward": reward.to_dict(),
        })

        try:
            await websocket.close()
        except Exception:
            pass

        # Cleanup voice clients
        if tts:
            try:
                await tts.close()
            except Exception:
                pass
        if stt:
            try:
                await stt.close()
            except Exception:
                pass
