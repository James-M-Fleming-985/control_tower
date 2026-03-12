"""Communication registers — formality and register models.

Registers govern the actor's language style, vocabulary complexity,
and interaction manner. Combined with the epistemological stance,
they produce the full personality of a conversation actor.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RegisterLevel(str, Enum):
    FORMAL = "formal"
    CONSULTATIVE = "consultative"
    CASUAL = "casual"
    SOCRATIC = "socratic"
    ADVERSARIAL = "adversarial"


@dataclass(frozen=True)
class CommunicationRegister:
    """Defines the linguistic register an actor uses."""

    level: RegisterLevel
    label: str
    description: str
    vocabulary_guidance: str
    tone_guidance: str
    interaction_style: str

    def to_system_prompt_fragment(self) -> str:
        return (
            f"Communicate in a {self.label.lower()} register. "
            f"{self.description} "
            f"Vocabulary: {self.vocabulary_guidance}. "
            f"Tone: {self.tone_guidance}. "
            f"Style: {self.interaction_style}."
        )


# ── Built-in register definitions ────────────────────────────────────

FORMAL = CommunicationRegister(
    level=RegisterLevel.FORMAL,
    label="Formal",
    description="Use precise, academic language with complete sentences and structured argumentation.",
    vocabulary_guidance="Use technical philosophical terminology freely; define terms where ambiguity exists",
    tone_guidance="Measured, respectful, and authoritative",
    interaction_style="Structured turn-taking with clear thesis-support-conclusion patterns",
)

CONSULTATIVE = CommunicationRegister(
    level=RegisterLevel.CONSULTATIVE,
    label="Consultative",
    description="Maintain a professional but accessible tone, suitable for mentoring or coaching.",
    vocabulary_guidance="Use accessible language with occasional technical terms, always explained",
    tone_guidance="Warm but professional, encouraging yet challenging",
    interaction_style="Guided exploration with check-in questions and supportive feedback",
)

CASUAL = CommunicationRegister(
    level=RegisterLevel.CASUAL,
    label="Casual",
    description="Use everyday language and a relaxed conversational style, while keeping intellectual depth.",
    vocabulary_guidance="Everyday language; use analogies and examples over technical jargon",
    tone_guidance="Friendly, approachable, and curious",
    interaction_style="Free-flowing dialogue with natural tangents and collaborative discovery",
)

SOCRATIC = CommunicationRegister(
    level=RegisterLevel.SOCRATIC,
    label="Socratic",
    description="Primarily ask questions to lead the interlocutor to discover insights themselves.",
    vocabulary_guidance="Clear and direct; questions should be precisely worded",
    tone_guidance="Curious, gently probing, non-judgmental",
    interaction_style="Question-driven dialogue; rarely state conclusions, instead guide through questions",
)

ADVERSARIAL = CommunicationRegister(
    level=RegisterLevel.ADVERSARIAL,
    label="Adversarial",
    description="Challenge positions firmly, Playing devil's advocate to stress-test arguments.",
    vocabulary_guidance="Direct and incisive; use counter-examples freely",
    tone_guidance="Challenging but respectful; provocative without being hostile",
    interaction_style="Rapid counter-arguments, demand for stronger evidence, expose weak reasoning",
)


REGISTER_REGISTRY: dict[RegisterLevel, CommunicationRegister] = {
    RegisterLevel.FORMAL: FORMAL,
    RegisterLevel.CONSULTATIVE: CONSULTATIVE,
    RegisterLevel.CASUAL: CASUAL,
    RegisterLevel.SOCRATIC: SOCRATIC,
    RegisterLevel.ADVERSARIAL: ADVERSARIAL,
}


def get_register(level: RegisterLevel | str) -> CommunicationRegister:
    if isinstance(level, str):
        level = RegisterLevel(level)
    return REGISTER_REGISTRY[level]
