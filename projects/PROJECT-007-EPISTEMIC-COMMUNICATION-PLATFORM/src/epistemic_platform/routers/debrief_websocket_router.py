"""Debrief WebSocket router — /ws/debrief/{session_id} endpoint.

Handles interactive coach debrief after a conversation session completes.
Premium-only feature — checks subscription_tier before allowing connection.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, status

from epistemic_platform.auth import decode_token
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


@router.websocket("/ws/debrief/{session_id}")
async def debrief_websocket(
    websocket: WebSocket,
    session_id: int,
    token: str | None = None,
):
    """WebSocket endpoint for interactive coach debrief.

    Connect: ws://host/ws/debrief/{session_id}?token=<jwt>

    Server sends on connect:
        {"type": "debrief_start"}
        {"type": "stream_start"}
        {"type": "stream_delta", "content": "..."}
        {"type": "stream_end"}

    Client sends:
        {"type": "message", "content": "user reflection text"}
        {"type": "end_debrief"}

    Server sends on message:
        {"type": "stream_start"}
        {"type": "stream_delta", "content": "..."}
        {"type": "stream_end"}
    """
    # 1. Authenticate
    user_id = _authenticate_ws(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    await websocket.accept()

    async with async_session_factory() as db:
        # 2. Load user and verify premium
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

        # 5. Create debrief session in DB
        debrief_session = ConversationSession(
            user_id=user_id,
            actor_id=parent_session.actor_id,
            scenario_id=parent_session.scenario_id,
            parent_session_id=parent_session.id,
            status="active",
            mode="text",
            messages=[],
            coaching_annotations=[],
            trilemma_state={},
            turn_count=0,
            started_at=datetime.now(timezone.utc),
        )
        db.add(debrief_session)
        await db.flush()

        # 6. Create coach debrief engine
        coaching_llm = ClaudeCoachingAdapter()
        debrief = CoachDebrief(
            coaching_llm=coaching_llm,
            reward=reward,
            parent_messages=parent_session.messages or [],
        )

        # 7. Send opening message
        await websocket.send_json({"type": "debrief_start", "session_id": debrief_session.id})
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

        # Store opening message
        debrief_session.messages = [
            *debrief_session.messages,
            {"role": "assistant", "content": opening_text},
        ]
        await db.flush()

        # 8. Message loop
        try:
            while not debrief.is_complete:
                raw = await websocket.receive_text()
                data = json.loads(raw)
                msg_type = data.get("type", "")

                if msg_type == "end_debrief":
                    break

                if msg_type == "message":
                    content = data.get("content", "").strip()
                    if not content:
                        continue

                    # Store user message
                    debrief_session.messages = [
                        *debrief_session.messages,
                        {"role": "user", "content": content},
                    ]
                    debrief_session.turn_count += 1
                    await db.flush()

                    # Stream coach response
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

                    # Store coach response
                    debrief_session.messages = [
                        *debrief_session.messages,
                        {"role": "assistant", "content": response_text},
                    ]
                    await db.flush()

        except Exception as e:
            logger.warning("Debrief WebSocket error for session %d: %s", session_id, e)

        # 9. End debrief session
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
