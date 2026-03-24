"""ExpressiveState — bridges conversation engine to voice/avatar output.

The conversation engine produces an ExpressiveState after each actor turn.
The PresentationRenderer consumes it to set voice prosody parameters
(ElevenLabs) and, in future, avatar facial expressions and gestures.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Tone(str, Enum):
    NEUTRAL = "neutral"
    WARM = "warm"
    CHALLENGING = "challenging"
    ENCOURAGING = "encouraging"
    SKEPTICAL = "skeptical"
    CURIOUS = "curious"
    AUTHORITATIVE = "authoritative"


class Mood(str, Enum):
    CALM = "calm"
    ENGAGED = "engaged"
    INTENSE = "intense"
    REFLECTIVE = "reflective"
    PLAYFUL = "playful"


class Energy(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ExpressiveState:
    """Current expressive state of the actor for a given turn."""

    tone: Tone = Tone.NEUTRAL
    mood: Mood = Mood.CALM
    energy: Energy = Energy.MEDIUM
    urgency: float = 0.5  # 0.0 (no urgency) → 1.0 (very urgent)
    connotation: float = 0.5  # 0.0 (negative) → 1.0 (positive)

    def to_voice_params(self) -> dict:
        """Map expressive state to ElevenLabs voice parameters."""
        stability = 0.5
        similarity_boost = 0.75
        style = 0.0

        # Tone adjustments
        if self.tone in (Tone.WARM, Tone.ENCOURAGING):
            stability += 0.1
            style += 0.3
        elif self.tone in (Tone.CHALLENGING, Tone.SKEPTICAL):
            stability -= 0.1
            style += 0.2
        elif self.tone == Tone.AUTHORITATIVE:
            stability += 0.2

        # Energy adjustments
        if self.energy == Energy.HIGH:
            stability -= 0.15
            style += 0.2
        elif self.energy == Energy.LOW:
            stability += 0.15
            style -= 0.1

        # Urgency adjustments
        if self.urgency > 0.7:
            stability -= 0.1
            style += 0.15

        return {
            "stability": max(0.0, min(1.0, stability)),
            "similarity_boost": similarity_boost,
            "style": max(0.0, min(1.0, style)),
        }

    def to_avatar_params(self) -> dict:
        """Map expressive state to avatar parameters (future use)."""
        return {
            "facial_expression": self.tone.value,
            "body_energy": self.energy.value,
            "mood_intensity": self.mood.value,
            "valence": self.connotation,
        }

    @classmethod
    def from_llm_metadata(cls, metadata: dict) -> ExpressiveState:
        """Parse expressive state from LLM response metadata."""
        return cls(
            tone=Tone(metadata.get("tone", "neutral")),
            mood=Mood(metadata.get("mood", "calm")),
            energy=Energy(metadata.get("energy", "medium")),
            urgency=float(metadata.get("urgency", 0.5)),
            connotation=float(metadata.get("connotation", 0.5)),
        )
