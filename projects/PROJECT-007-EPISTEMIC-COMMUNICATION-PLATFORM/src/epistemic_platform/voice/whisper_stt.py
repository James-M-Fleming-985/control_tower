"""Whisper STT client — transcribes audio bytes to text via OpenAI API."""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Result of a speech-to-text transcription."""

    text: str
    language: str | None = None
    duration: float | None = None


class WhisperSTTClient:
    """Async OpenAI Whisper speech-to-text client."""

    def __init__(self, api_key: str, model: str = "whisper-1") -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def transcribe(
        self, audio_bytes: bytes, audio_format: str = "webm"
    ) -> TranscriptionResult:
        """Transcribe audio bytes to text.

        Parameters
        ----------
        audio_bytes : raw audio data
        audio_format : file extension hint (webm, wav, mp3, etc.)
        """
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = f"audio.{audio_format}"

        logger.debug("Transcribing %d bytes of %s audio", len(audio_bytes), audio_format)
        try:
            response = await self._client.audio.transcriptions.create(
                model=self._model,
                file=audio_file,
                response_format="verbose_json",
            )
        except Exception:
            logger.exception("Whisper API call failed")
            raise

        return TranscriptionResult(
            text=response.text.strip(),
            language=getattr(response, "language", None),
            duration=getattr(response, "duration", None),
        )

    async def close(self) -> None:
        await self._client.close()
