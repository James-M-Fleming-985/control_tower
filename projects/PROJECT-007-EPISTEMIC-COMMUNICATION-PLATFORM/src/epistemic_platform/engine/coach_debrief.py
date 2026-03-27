"""Coach debrief — interactive post-session coaching conversation.

After a prescribed conversation session completes, premium users can enter
an interactive coach debrief powered by Claude Opus.  The coach reviews
the session transcript, the dialogue analysis, and the session score,
then engages in a reflective conversation with the user.

The debrief is stored as a separate ConversationSession with
parent_session_id pointing to the original session.
"""

from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator

from epistemic_platform.engine.achievement_engine import SessionReward
from epistemic_platform.llm.protocol import CoachingLLM, LLMMessage, LLMStreamChunk

logger = logging.getLogger(__name__)

# Maximum debrief turns before auto-close
_MAX_DEBRIEF_TURNS = 10


def build_debrief_system_prompt(
    reward: SessionReward,
    messages: list[dict],
) -> str:
    """Build the system prompt for the coach debrief conversation.

    Includes session transcript summary, scores, and analysis so the coach
    has full context.
    """
    analysis = reward.analysis
    score = reward.score

    # Truncate transcript to last 40 messages, 500 chars each
    recent = messages[-40:]
    transcript_lines = []
    for m in recent:
        role = m.get("role", "unknown").upper()
        content = m.get("content", "")[:500]
        transcript_lines.append(f"{role}: {content}")
    transcript = "\n".join(transcript_lines)

    sections = [
        "You are an epistemological communication coach conducting a post-session debrief.",
        "Your role is to help the user reflect on their conversation, identify patterns,",
        "and develop strategies for improvement. Be warm, specific, and actionable.",
        "",
        "## Session Summary",
        f"- Total turns: {analysis.total_turns}" if analysis else "",
        f"- Grade: {score.grade} (score: {score.final_score:.0f}/100)" if score else "",
        f"- Gricean quality: {score.gricean_score:.0f}/100" if score else "",
        f"- Trilemma navigation: {score.trilemma_score:.0f}/100" if score else "",
        f"- Flexibility: {score.flexibility_score:.0f}/100" if score else "",
    ]

    if analysis:
        if analysis.gricean_improvement != 0:
            sections.append(f"- Gricean improvement during session: {analysis.gricean_improvement:+.1f}")
        if analysis.trilemma.horns_escaped > 0:
            sections.append(f"- Horns escaped: {analysis.trilemma.horns_escaped}/{analysis.trilemma.horns_visited}")
        if analysis.stance.primary_stance:
            sections.append(f"- Primary stance detected: {analysis.stance.primary_stance}")
        if analysis.avg_composure is not None:
            sections.append(f"- Average composure: {analysis.avg_composure:.0%}")

    sections.extend([
        "",
        "## Recent Transcript",
        transcript,
        "",
        "## Coaching Guidelines",
        "1. Start by highlighting one specific strength — cite a direct quote or moment from the transcript",
        "2. Ask reflective questions — don't lecture",
        "3. Connect observations to epistemological concepts (stances, trilemma, Gricean maxims)",
        "4. Suggest one concrete thing to try in the next session",
        "5. Keep responses concise — 2-3 short paragraphs maximum",
        "6. If the user wants to end, wrap up warmly with encouragement",
        "7. NEVER repeat or paraphrase the same observation twice within a response",
        "8. Each sentence must advance a new idea — no filler or restatement",
        "9. Be specific: reference direct quotes or observable moments, not vague generalities",
        "10. Offer a brief real-world exercise the user can try outside the platform — e.g. 'This week, when someone disagrees with you at work, pause and steelman their view before responding.' Tailor the exercise to the specific weakness you identified in the session.",
    ])

    return "\n".join(sections)


class CoachDebrief:
    """Manages an interactive coach debrief conversation."""

    def __init__(
        self,
        coaching_llm: CoachingLLM,
        reward: SessionReward,
        parent_messages: list[dict],
        *,
        existing_messages: list[dict] | None = None,
    ) -> None:
        self._llm = coaching_llm
        self._system_prompt = build_debrief_system_prompt(reward, parent_messages)
        if existing_messages:
            self._messages = list(existing_messages)
            self._turn_count = sum(1 for m in existing_messages if m.get("role") == "user")
        else:
            self._messages = []
            self._turn_count = 0

    @property
    def turn_count(self) -> int:
        return self._turn_count

    @property
    def is_complete(self) -> bool:
        return self._turn_count >= _MAX_DEBRIEF_TURNS

    async def handle_message(self, user_text: str) -> AsyncIterator[LLMStreamChunk]:
        """Process a user message and yield streamed coach response.

        Yields
        ------
        LLMStreamChunk with coach response deltas.
        """
        self._messages.append({"role": "user", "content": user_text})
        self._turn_count += 1

        llm_messages = [
            LLMMessage(role=m["role"], content=m["content"])
            for m in self._messages
        ]

        full_response = ""
        async for chunk in self._llm.analyse_stream(
            messages=llm_messages,
            system_prompt=self._system_prompt,
            max_tokens=1024,
        ):
            if chunk.delta:
                full_response += chunk.delta
            yield chunk

        self._messages.append({"role": "assistant", "content": full_response})

    async def get_opening_message(self) -> AsyncIterator[LLMStreamChunk]:
        """Generate the coach's opening message to start the debrief.

        Yields
        ------
        LLMStreamChunk with opening message deltas.
        """
        opening_prompt = (
            "The user has just completed a conversation session. "
            "Start the debrief by citing one specific moment from the transcript "
            "where they demonstrated a strength, then ask a focused reflective "
            "question about that moment. Keep your response to 2-3 short paragraphs."
        )

        llm_messages = [LLMMessage(role="user", content=opening_prompt)]

        full_response = ""
        async for chunk in self._llm.analyse_stream(
            messages=llm_messages,
            system_prompt=self._system_prompt,
            max_tokens=1024,
        ):
            if chunk.delta:
                full_response += chunk.delta
            yield chunk

        self._messages.append({"role": "assistant", "content": full_response})
