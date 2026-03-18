"""WebSocket connection manager — handles concurrent session connections.

Manages the lifecycle of WebSocket connections, mapping each to a
ConversationManager instance for session isolation.
"""

from __future__ import annotations

import logging

from fastapi import WebSocket

from epistemic_platform.config import get_settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections mapped to conversation sessions."""

    def __init__(self) -> None:
        # session_id -> WebSocket
        self._connections: dict[int, WebSocket] = {}

    @property
    def active_count(self) -> int:
        return len(self._connections)

    async def connect(self, session_id: int, websocket: WebSocket) -> bool:
        """Accept a WebSocket connection for a session.

        Returns False if max concurrent sessions exceeded.
        """
        settings = get_settings()
        if self.active_count >= settings.max_concurrent_sessions:
            logger.warning(
                "Max concurrent sessions (%d) reached, rejecting session %d",
                settings.max_concurrent_sessions,
                session_id,
            )
            await websocket.close(code=1013, reason="Server busy")
            return False

        if session_id in self._connections:
            # Close existing connection for this session (reconnect scenario)
            await self.disconnect(session_id, code=1000, reason="Replaced by new connection")

        await websocket.accept()
        self._connections[session_id] = websocket
        logger.info("WebSocket connected: session_id=%d (active=%d)", session_id, self.active_count)
        return True

    async def disconnect(self, session_id: int, code: int = 1000, reason: str = "") -> None:
        """Remove and close a WebSocket connection."""
        ws = self._connections.pop(session_id, None)
        if ws:
            try:
                await ws.close(code=code, reason=reason)
            except Exception:
                pass  # Already closed
            logger.info("WebSocket disconnected: session_id=%d (active=%d)", session_id, self.active_count)

    def get(self, session_id: int) -> WebSocket | None:
        """Get the WebSocket for a session, if connected."""
        return self._connections.get(session_id)

    async def send_json(self, session_id: int, data: dict) -> bool:
        """Send a JSON message to a specific session. Returns False if not connected."""
        ws = self._connections.get(session_id)
        if not ws:
            return False
        try:
            await ws.send_json(data)
            return True
        except Exception:
            await self.disconnect(session_id)
            return False

    async def send_text(self, session_id: int, text: str) -> bool:
        """Send a text message to a specific session."""
        ws = self._connections.get(session_id)
        if not ws:
            return False
        try:
            await ws.send_text(text)
            return True
        except Exception:
            await self.disconnect(session_id)
            return False

    async def broadcast_json(self, data: dict) -> None:
        """Broadcast a JSON message to all connected sessions."""
        for session_id in list(self._connections.keys()):
            await self.send_json(session_id, data)

    async def shutdown(self) -> None:
        """Close all connections (used during app shutdown)."""
        for session_id in list(self._connections.keys()):
            await self.disconnect(session_id, code=1001, reason="Server shutting down")


# Singleton instance
manager = ConnectionManager()
