"""WebSocket router — /ws/conversation/{session_id} endpoint.

Handles real-time conversation over WebSocket with streamed actor responses
and coaching updates pushed asynchronously.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.auth import decode_token
from epistemic_platform.database import get_db, async_session_factory
from epistemic_platform.engine.connection_manager import manager
from epistemic_platform.engine.conversation_manager import ConversationManager
from epistemic_platform.llm.claude_adapter import ClaudeConversationAdapter, ClaudeCoachingAdapter
from epistemic_platform.repositories.actor_profile_repository import ActorProfileRepository
from epistemic_platform.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)

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


@router.websocket("/ws/conversation/{session_id}")
async def conversation_websocket(
    websocket: WebSocket,
    session_id: int,
    token: str | None = None,
):
    """WebSocket endpoint for real-time conversation.

    Connect with: ws://host/ws/conversation/{session_id}?token=<jwt>

    Client sends JSON:
        {"type": "message", "content": "user text here"}
        {"type": "end_session"}

    Server sends JSON:
        {"type": "stream_start"}
        {"type": "stream_delta", "content": "text chunk"}
        {"type": "stream_end"}
        {"type": "coaching", "annotation": {...}}
        {"type": "error", "detail": "..."}
        {"type": "session_ended"}
    """
    # 1. Authenticate via query param token
    user_id = _authenticate_ws(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    # 2. Accept connection
    connected = await manager.connect(session_id, websocket)
    if not connected:
        return

    # 3. Load session and actor from DB
    async with async_session_factory() as db:
        session_repo = ConversationSessionRepository(db)
        session = await session_repo.get(session_id)

        if not session:
            await manager.send_json(session_id, {"type": "error", "detail": "Session not found"})
            await manager.disconnect(session_id)
            return

        if session.user_id != user_id:
            await manager.send_json(session_id, {"type": "error", "detail": "Not your session"})
            await manager.disconnect(session_id)
            return

        if session.status != "active":
            await manager.send_json(session_id, {"type": "error", "detail": "Session not active"})
            await manager.disconnect(session_id)
            return

        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(session.actor_id)
        if not actor:
            await manager.send_json(session_id, {"type": "error", "detail": "Actor not found"})
            await manager.disconnect(session_id)
            return

        # 4. Create conversation manager
        conversation_llm = ClaudeConversationAdapter()
        coaching_llm = ClaudeCoachingAdapter()

        conv_manager = ConversationManager(
            session=session,
            actor=actor,
            conversation_llm=conversation_llm,
            coaching_llm=coaching_llm,
            db=db,
        )

        # 5. Message loop
        try:
            while True:
                raw = await websocket.receive_text()
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    await manager.send_json(session_id, {
                        "type": "error",
                        "detail": "Invalid JSON",
                    })
                    continue

                msg_type = msg.get("type")

                if msg_type == "end_session":
                    await conv_manager.end_session()
                    await manager.send_json(session_id, {"type": "session_ended"})
                    break

                if msg_type == "message":
                    content = msg.get("content", "").strip()
                    if not content:
                        await manager.send_json(session_id, {
                            "type": "error",
                            "detail": "Empty message",
                        })
                        continue

                    # Stream actor response
                    await manager.send_json(session_id, {"type": "stream_start"})

                    async for chunk in conv_manager.handle_user_message(content):
                        if chunk.delta:
                            await manager.send_json(session_id, {
                                "type": "stream_delta",
                                "content": chunk.delta,
                            })

                    await manager.send_json(session_id, {"type": "stream_end"})

                    # Check coaching trigger
                    annotation = await conv_manager.maybe_run_coaching()
                    if annotation:
                        await manager.send_json(session_id, {
                            "type": "coaching",
                            "annotation": annotation.to_dict(),
                        })

                else:
                    await manager.send_json(session_id, {
                        "type": "error",
                        "detail": f"Unknown message type: {msg_type}",
                    })

        except WebSocketDisconnect:
            logger.info("Client disconnected: session_id=%d", session_id)
        except Exception as e:
            logger.exception("WebSocket error for session %d: %s", session_id, e)
            await manager.send_json(session_id, {
                "type": "error",
                "detail": "Internal server error",
            })
        finally:
            await manager.disconnect(session_id)
