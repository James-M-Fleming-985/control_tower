"""LLM protocol — defines the interface that all LLM adapters must implement."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import AsyncIterator, Protocol, runtime_checkable


@dataclass
class LLMMessage:
    """A single message in the conversation history."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Complete (non-streaming) response from the LLM."""

    content: str
    model: str
    usage: dict = field(default_factory=dict)
    raw_metadata: dict = field(default_factory=dict)


@dataclass
class LLMStreamChunk:
    """A single chunk from a streaming response."""

    delta: str
    is_final: bool = False
    usage: dict | None = None


@runtime_checkable
class EpistemicActorLLM(Protocol):
    """Protocol for conversation LLM — generates actor responses (streaming)."""

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[LLMStreamChunk]: ...

    async def generate(
        self,
        messages: list[LLMMessage],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse: ...


@runtime_checkable
class CoachingLLM(Protocol):
    """Protocol for coaching LLM — analyses conversation and gives feedback."""

    async def analyse(
        self,
        messages: list[LLMMessage],
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse: ...

    async def analyse_stream(
        self,
        messages: list[LLMMessage],
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> AsyncIterator[LLMStreamChunk]: ...
