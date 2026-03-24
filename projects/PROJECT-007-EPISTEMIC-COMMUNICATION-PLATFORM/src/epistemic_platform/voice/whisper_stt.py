"""Whisper STT client — transcribes audio bytes to text via OpenAI API."""

from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Common Whisper hallucination patterns on silence/noise/filler sounds
_HALLUCINATION_RE = re.compile(
    r"^[\s♪♫🎵🎶\-–—.…,!?]+$"  # music symbols / punctuation only
    r"|(?:thank you for watching|please subscribe|like and subscribe"
    r"|thanks for watching|copyright|subtitles by)",
    re.IGNORECASE,
)


@dataclass
class TranscriptionResult:
    """Result of a speech-to-text transcription."""

    text: str
    language: str | None = None
    duration: float | None = None
    no_speech_prob: float = 0.0


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
        if len(audio_bytes) < 1000:
            logger.warning("Audio too short (%d bytes), skipping STT", len(audio_bytes))
            return TranscriptionResult(text="", language=None, duration=0.0)

        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = f"audio.{audio_format}"

        logger.debug("Transcribing %d bytes of %s audio", len(audio_bytes), audio_format)
        try:
            response = await self._client.audio.transcriptions.create(
                model=self._model,
                file=audio_file,
                response_format="verbose_json",
                language="en",
            )
        except Exception:
            logger.exception("Whisper API call failed")
            raise

        text = response.text.strip()

        # Extract no_speech_prob from first segment (if available)
        no_speech_prob = 0.0
        segments = getattr(response, "segments", None)
        if segments and len(segments) > 0:
            no_speech_prob = getattr(segments[0], "no_speech_prob", 0.0) or 0.0

        # Filter hallucinated transcriptions
        if no_speech_prob > 0.4:
            logger.info("Filtering high no_speech_prob (%.2f): '%s'", no_speech_prob, text)
            text = ""
        elif _HALLUCINATION_RE.search(text):
            logger.info("Filtering hallucinated transcription: '%s'", text)
            text = ""
        elif len(text) > 0 and not any(c.isalnum() for c in text):
            logger.info("Filtering non-alphanumeric transcription: '%s'", text)
            text = ""

        return TranscriptionResult(
            text=text,
            language=getattr(response, "language", None),
            duration=getattr(response, "duration", None),
            no_speech_prob=no_speech_prob,
        )

    async def close(self) -> None:
        await self._client.close()
