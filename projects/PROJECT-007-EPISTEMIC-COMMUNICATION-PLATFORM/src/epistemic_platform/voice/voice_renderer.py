"""VoiceRenderer — converts actor text + ExpressiveState to streaming audio.

Implements the PresentationRenderer protocol using ElevenLabs TTS.
Falls back to text-only RenderResult when TTS is unavailable.
"""

from __future__ import annotations

import logging
from typing import AsyncIterator

from epistemic_platform.ontology.expressive_state import ExpressiveState
from epistemic_platform.voice.elevenlabs_tts import ElevenLabsTTSClient
from epistemic_platform.voice.protocol import RenderResult

logger = logging.getLogger(__name__)


class VoiceRenderer:
    """Renders actor responses as audio via ElevenLabs TTS."""

    def __init__(self, tts_client: ElevenLabsTTSClient) -> None:
        self._tts = tts_client

    @property
    def modality(self) -> str:
        return "voice"

    async def render(
        self,
        text: str,
        expressive_state: ExpressiveState,
    ) -> RenderResult:
        """Render complete text to a single audio result."""
        voice_params = expressive_state.to_voice_params()
        try:
            audio_data = await self._tts.synthesize(text, voice_params)
        except Exception:
            logger.exception("TTS synthesis failed, falling back to text-only")
            return RenderResult(
                modality="text",
                text_content=text,
                metadata={"fallback": True},
            )

        return RenderResult(
            modality="voice",
            text_content=text,
            audio_data=audio_data,
            metadata={
                "tone": expressive_state.tone.value,
                "mood": expressive_state.mood.value,
                "energy": expressive_state.energy.value,
            },
        )

    async def render_stream(
        self,
        text_stream: AsyncIterator[str],
        expressive_state: ExpressiveState,
    ) -> AsyncIterator[RenderResult]:
        """Collect streamed text then stream TTS audio chunks.

        Text is collected first because ElevenLabs needs complete sentences
        for natural prosody. Each audio chunk is yielded as a RenderResult.
        Text-only RenderResults are also yielded for real-time subtitle display.
        """
        full_text = ""
        async for chunk in text_stream:
            full_text += chunk
            yield RenderResult(modality="text", text_content=chunk)

        if not full_text.strip():
            return

        voice_params = expressive_state.to_voice_params()
        try:
            async for audio_chunk in self._tts.synthesize_stream(
                full_text, voice_params
            ):
                yield RenderResult(
                    modality="voice",
                    text_content="",
                    audio_data=audio_chunk,
                    metadata={
                        "tone": expressive_state.tone.value,
                        "mood": expressive_state.mood.value,
                        "energy": expressive_state.energy.value,
                    },
                )
        except Exception:
            logger.exception("TTS streaming failed")
            yield RenderResult(
                modality="text",
                text_content="",
                metadata={"tts_error": True},
            )
