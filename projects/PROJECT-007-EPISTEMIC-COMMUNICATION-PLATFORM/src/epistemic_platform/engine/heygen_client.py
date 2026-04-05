"""HeyGen Streaming Avatar API client.

Manages interactive avatar sessions — create, speak, interrupt, stop.
Uses TaskType.REPEAT so HeyGen speaks our LLM text verbatim (no HeyGen LLM).
HeyGen uses ElevenLabs TTS internally with the same voice IDs we configure per actor.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from epistemic_platform.config import get_settings

logger = logging.getLogger(__name__)

# Maps our ExpressiveState mood → HeyGen voice emotion presets
_MOOD_TO_EMOTION: dict[str, str] = {
    "enthusiastic": "excited",
    "excited": "excited",
    "warm": "friendly",
    "friendly": "friendly",
    "concerned": "serious",
    "serious": "serious",
    "calm": "soothing",
    "thoughtful": "soothing",
    "assertive": "broadcaster",
    "challenging": "broadcaster",
}


class HeyGenClient:
    """Async client for HeyGen Streaming Avatar API."""

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.heygen_api_key
        self._base = settings.heygen_api_base.rstrip("/")
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={"x-api-key": self._api_key, "Content-Type": "application/json"},
        )

    async def list_avatars(self) -> list[dict[str, Any]]:
        """List all available avatars (stock + custom).

        Returns list of dicts with avatar_id, avatar_name, gender, preview_url, etc.
        """
        resp = await self._client.get(f"{self._base}/v1/avatar.list")
        resp.raise_for_status()
        data = resp.json().get("data", {})
        avatars = data.get("avatars", [])
        logger.info("HeyGen: fetched %d avatars", len(avatars))
        return avatars

    async def create_token(self) -> str:
        """Get a one-time access token for streaming session."""
        resp = await self._client.post(f"{self._base}/v1/streaming.create_token")
        resp.raise_for_status()
        data = resp.json()
        return data["data"]["token"]

    async def create_session(
        self,
        avatar_id: str,
        voice_id: str,
        quality: str = "medium",
    ) -> dict[str, Any]:
        """Create a new streaming avatar session.

        Returns dict with session_id, access_token, url (LiveKit server).
        """
        token = await self.create_token()

        resp = await self._client.post(
            f"{self._base}/v1/streaming.new",
            json={
                "avatar_id": avatar_id,
                "voice": {
                    "voiceId": voice_id,
                    "rate": 1.0,
                    "emotion": "friendly",
                },
                "quality": quality,
            },
            headers={
                "x-api-key": self._api_key,
                "Authorization": f"Bearer {token}",
            },
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        logger.info(
            "HeyGen session created: session_id=%s", data.get("session_id")
        )
        return {
            "session_id": data["session_id"],
            "access_token": data["access_token"],
            "url": data["url"],
        }

    async def start_session(self, session_id: str) -> None:
        """Signal avatar to begin (starts idle animation)."""
        resp = await self._client.post(
            f"{self._base}/v1/streaming.start",
            json={"session_id": session_id},
        )
        resp.raise_for_status()
        logger.info("HeyGen session started: %s", session_id)

    async def speak(
        self,
        session_id: str,
        text: str,
        emotion: str | None = None,
    ) -> None:
        """Make the avatar speak text verbatim (TaskType.REPEAT).

        Args:
            session_id: Active session ID
            text: Text for avatar to speak (our LLM response, spoken verbatim)
            emotion: Optional HeyGen emotion preset
        """
        payload: dict[str, Any] = {
            "session_id": session_id,
            "text": text,
            "task_type": "repeat",  # Don't process through HeyGen's LLM
        }
        if emotion:
            payload["voice"] = {"emotion": emotion}

        resp = await self._client.post(
            f"{self._base}/v1/streaming.task",
            json=payload,
        )
        resp.raise_for_status()

    async def interrupt(self, session_id: str) -> None:
        """Interrupt current avatar speech (for barge-in)."""
        resp = await self._client.post(
            f"{self._base}/v1/streaming.interrupt",
            json={"session_id": session_id},
        )
        resp.raise_for_status()
        logger.debug("HeyGen speech interrupted: %s", session_id)

    async def stop_session(self, session_id: str) -> None:
        """Stop and destroy the streaming session."""
        try:
            resp = await self._client.post(
                f"{self._base}/v1/streaming.stop",
                json={"session_id": session_id},
            )
            resp.raise_for_status()
            logger.info("HeyGen session stopped: %s", session_id)
        except Exception:
            logger.warning("Failed to stop HeyGen session %s (may have expired)", session_id)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    @staticmethod
    def mood_to_emotion(mood: str | None) -> str | None:
        """Convert our ExpressiveState mood to HeyGen emotion preset."""
        if not mood:
            return None
        return _MOOD_TO_EMOTION.get(mood.lower())
