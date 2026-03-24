"""TextRenderer — plain text presentation (M0 default).

Simply passes through text content with no audio or avatar transformation.
Used for text-mode conversations and as a fallback.
"""

from __future__ import annotations

from typing import AsyncIterator

from epistemic_platform.ontology.expressive_state import ExpressiveState
from epistemic_platform.voice.protocol import RenderResult


class TextRenderer:
    """Renders actor responses as plain text."""

    @property
    def modality(self) -> str:
        return "text"

    async def render(
        self,
        text: str,
        expressive_state: ExpressiveState,
    ) -> RenderResult:
        return RenderResult(
            modality="text",
            text_content=text,
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
        async for chunk in text_stream:
            yield RenderResult(
                modality="text",
                text_content=chunk,
                metadata={
                    "tone": expressive_state.tone.value,
                    "mood": expressive_state.mood.value,
                    "energy": expressive_state.energy.value,
                },
            )
