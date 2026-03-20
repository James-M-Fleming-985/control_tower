"""ElevenLabs TTS client — converts text + voice params to streaming audio.

Uses httpx directly for predictable async behavior across SDK versions.
Voice params come from ExpressiveState.to_voice_params().
"""

from __future__ import annotations

import logging
from typing import AsyncIterator

import httpx

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.elevenlabs.io/v1"


class ElevenLabsTTSClient:
    """Async ElevenLabs text-to-speech client."""

    def __init__(self, api_key: str, voice_id: str, model_id: str) -> None:
        self._voice_id = voice_id
        self._model_id = model_id
        self._client = httpx.AsyncClient(
            base_url=_BASE_URL,
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
            timeout=30.0,
        )

    def _payload(self, text: str, voice_params: dict) -> dict:
        return {
            "text": text,
            "model_id": self._model_id,
            "voice_settings": {
                "stability": voice_params.get("stability", 0.5),
                "similarity_boost": voice_params.get("similarity_boost", 0.75),
                "style": voice_params.get("style", 0.0),
            },
        }

    async def synthesize(self, text: str, voice_params: dict) -> bytes:
        """Convert text to complete audio bytes (MP3)."""
        resp = await self._client.post(
            f"/text-to-speech/{self._voice_id}",
            json=self._payload(text, voice_params),
            headers={"Accept": "audio/mpeg"},
        )
        resp.raise_for_status()
        return resp.content

    async def synthesize_stream(
        self, text: str, voice_params: dict
    ) -> AsyncIterator[bytes]:
        """Convert text to streaming audio chunks (MP3)."""
        async with self._client.stream(
            "POST",
            f"/text-to-speech/{self._voice_id}/stream",
            json=self._payload(text, voice_params),
            headers={"Accept": "audio/mpeg"},
        ) as resp:
            resp.raise_for_status()
            async for chunk in resp.aiter_bytes(chunk_size=4096):
                yield chunk

    async def close(self) -> None:
        await self._client.aclose()
