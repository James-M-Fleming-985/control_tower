"""Context manager — manages conversation context window for LLM calls.

Implements a rolling window of recent messages plus a Sonnet-generated summary
of older messages when the window exceeds the configured threshold.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from epistemic_platform.config import get_settings
from epistemic_platform.llm.protocol import EpistemicActorLLM, LLMMessage


@dataclass
class ConversationContext:
    """Holds the current context window for a conversation session."""

    messages: list[dict] = field(default_factory=list)
    summary: str = ""
    max_window: int = 0

    def __post_init__(self):
        if self.max_window == 0:
            self.max_window = get_settings().context_window_max_messages

    @property
    def needs_summarisation(self) -> bool:
        """True if we have more messages than the window allows."""
        return len(self.messages) > self.max_window

    def get_llm_messages(self) -> list[LLMMessage]:
        """Build the LLM message list: optional summary + recent messages.

        Returns the summary (if any) as an initial assistant message,
        followed by the most recent messages within the window.
        """
        recent = self.messages[-self.max_window:]
        result: list[LLMMessage] = []

        if self.summary:
            result.append(LLMMessage(
                role="user",
                content="[Earlier conversation summary follows]",
            ))
            result.append(LLMMessage(
                role="assistant",
                content=f"[Summary of earlier conversation]\n{self.summary}",
            ))

        for msg in recent:
            result.append(LLMMessage(role=msg["role"], content=msg["content"]))

        return result

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the full history."""
        self.messages.append({"role": role, "content": content})


_SUMMARY_PROMPT = (
    "Summarise the following conversation in 3-5 sentences. "
    "Preserve key arguments, any epistemological positions taken, "
    "unresolved tensions, and the current direction of the dialogue. "
    "Write in third person (the user said X, the actor responded Y)."
)


async def summarise_overflow(
    context: ConversationContext,
    llm: EpistemicActorLLM,
) -> None:
    """If the context exceeds the window, summarise older messages in-place.

    Calls the conversation LLM (Sonnet) to produce a summary of messages
    that will be evicted from the window, then stores the summary and
    trims the message list.
    """
    if not context.needs_summarisation:
        return

    overflow_count = len(context.messages) - context.max_window
    overflow = context.messages[:overflow_count]

    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in overflow
    )

    # Include prior summary if it exists
    prior = f"Previous summary:\n{context.summary}\n\n" if context.summary else ""
    summary_input = f"{prior}New messages to summarise:\n{transcript}"

    response = await llm.generate(
        messages=[LLMMessage(role="user", content=summary_input)],
        system_prompt=_SUMMARY_PROMPT,
        temperature=0.3,
        max_tokens=512,
    )

    context.summary = response.content
    context.messages = context.messages[overflow_count:]
