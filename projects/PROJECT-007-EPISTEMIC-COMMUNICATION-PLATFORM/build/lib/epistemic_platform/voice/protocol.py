"""PresentationRenderer protocol — defines how actor responses are delivered.

TextRenderer (M0) → VoiceRenderer (M2) → AvatarRenderer (future).
The conversation engine calls render() and the appropriate renderer
converts the text + ExpressiveState into the target modality.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncIterator, Protocol, runtime_checkable

from epistemic_platform.ontology.expressive_state import ExpressiveState


@dataclass
class RenderResult:
    """Output of a render operation."""

    modality: str  # "text", "voice", "avatar"
    text_content: str
    audio_data: bytes | None = None
    avatar_data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


@runtime_checkable
class PresentationRenderer(Protocol):
    """Protocol for rendering actor responses."""

    @property
    def modality(self) -> str: ...

    async def render(
        self,
        text: str,
        expressive_state: ExpressiveState,
    ) -> RenderResult: ...

    async def render_stream(
        self,
        text_stream: AsyncIterator[str],
        expressive_state: ExpressiveState,
    ) -> AsyncIterator[RenderResult]: ...
