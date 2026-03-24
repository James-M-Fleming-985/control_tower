"""Claude adapter — implements EpistemicActorLLM and CoachingLLM using Anthropic API."""

from __future__ import annotations

from typing import AsyncIterator

import anthropic

from epistemic_platform.config import get_settings
from epistemic_platform.llm.protocol import (
    CoachingLLM,
    EpistemicActorLLM,
    LLMMessage,
    LLMResponse,
    LLMStreamChunk,
)


class ClaudeConversationAdapter:
    """Claude Sonnet adapter for conversation (streaming)."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.claude_sonnet_model
        self._default_temp = settings.claude_conversation_temperature

    def _build_messages(self, messages: list[LLMMessage]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        system_prompt: str,
        temperature: float | None = None,
        max_tokens: int = 1024,
    ) -> AsyncIterator[LLMStreamChunk]:
        temp = temperature if temperature is not None else self._default_temp
        async with self._client.messages.stream(
            model=self._model,
            system=system_prompt,
            messages=self._build_messages(messages),
            temperature=temp,
            max_tokens=max_tokens,
        ) as stream:
            async for text in stream.text_stream:
                yield LLMStreamChunk(delta=text)

            final_message = await stream.get_final_message()
            yield LLMStreamChunk(
                delta="",
                is_final=True,
                usage={
                    "input_tokens": final_message.usage.input_tokens,
                    "output_tokens": final_message.usage.output_tokens,
                },
            )

    async def generate(
        self,
        messages: list[LLMMessage],
        system_prompt: str,
        temperature: float | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        temp = temperature if temperature is not None else self._default_temp
        response = await self._client.messages.create(
            model=self._model,
            system=system_prompt,
            messages=self._build_messages(messages),
            temperature=temp,
            max_tokens=max_tokens,
        )
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )


class ClaudeCoachingAdapter:
    """Claude Opus adapter for coaching analysis (non-streaming)."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.claude_opus_model
        self._default_temp = settings.claude_coaching_temperature

    def _build_messages(self, messages: list[LLMMessage]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]

    async def analyse(
        self,
        messages: list[LLMMessage],
        system_prompt: str,
        temperature: float | None = None,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        temp = temperature if temperature is not None else self._default_temp
        response = await self._client.messages.create(
            model=self._model,
            system=system_prompt,
            messages=self._build_messages(messages),
            temperature=temp,
            max_tokens=max_tokens,
        )
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )
