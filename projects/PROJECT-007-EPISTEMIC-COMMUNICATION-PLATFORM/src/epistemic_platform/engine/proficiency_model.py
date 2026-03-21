"""Proficiency model — 4-axis skill tracking.

Tracks user proficiency across four axes:
1. Awareness   — trilemma navigation + epistemological self-awareness
2. Quality     — Gricean maxim adherence (communication quality)
3. Flexibility — stance diversity + adaptability
4. Composure   — vocal composure under pressure (voice sessions)

Each axis is 0.0–1.0.  Updated after every completed session using an
exponentially weighted moving average (EWMA) to balance recency with history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from epistemic_platform.engine.dialogue_analyser import DialogueAnalysis
from epistemic_platform.engine.scoring_rubric import SessionScore

# EWMA smoothing factor: higher = more weight on recent session
_ALPHA = 0.3


@dataclass
class ProficiencyAxis:
    """A single proficiency axis with current value and history."""

    name: str
    value: float = 0.0  # 0.0–1.0
    history: list[float] = field(default_factory=list)

    def update(self, new_value: float) -> None:
        """Update axis with EWMA."""
        clamped = max(0.0, min(1.0, new_value))
        if self.value == 0.0 and not self.history:
            # First data point — set directly
            self.value = clamped
        else:
            self.value = _ALPHA * clamped + (1 - _ALPHA) * self.value
        self.history.append(round(self.value, 3))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": round(self.value, 3),
            "history": self.history[-20:],  # Keep last 20 data points
        }


@dataclass
class ProficiencyProfile:
    """Complete 4-axis proficiency profile for a user."""

    awareness: ProficiencyAxis = field(default_factory=lambda: ProficiencyAxis(name="awareness"))
    quality: ProficiencyAxis = field(default_factory=lambda: ProficiencyAxis(name="quality"))
    flexibility: ProficiencyAxis = field(default_factory=lambda: ProficiencyAxis(name="flexibility"))
    composure: ProficiencyAxis = field(default_factory=lambda: ProficiencyAxis(name="composure"))

    @property
    def overall(self) -> float:
        """Weighted overall proficiency (composure optional)."""
        axes = [self.awareness, self.quality, self.flexibility]
        total = sum(a.value for a in axes)
        count = 3
        if self.composure.history:  # Only include if user has voice data
            total += self.composure.value
            count = 4
        return round(total / count, 3) if count > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "awareness": self.awareness.to_dict(),
            "quality": self.quality.to_dict(),
            "flexibility": self.flexibility.to_dict(),
            "composure": self.composure.to_dict(),
            "overall": self.overall,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProficiencyProfile:
        """Restore from stored JSON."""
        profile = cls()
        for axis_name in ("awareness", "quality", "flexibility", "composure"):
            axis_data = data.get(axis_name, {})
            axis = getattr(profile, axis_name)
            axis.value = float(axis_data.get("value", 0.0))
            axis.history = list(axis_data.get("history", []))
        return profile


class ProficiencyModel:
    """Updates a user's 4-axis proficiency profile after each session."""

    def update(
        self,
        profile: ProficiencyProfile,
        analysis: DialogueAnalysis,
        score: SessionScore,
    ) -> ProficiencyProfile:
        """Update proficiency axes based on session performance.

        Parameters
        ----------
        profile : ProficiencyProfile
            Current proficiency state (mutated in place and returned).
        analysis : DialogueAnalysis
            Current session analysis.
        score : SessionScore
            Current session score.

        Returns
        -------
        Updated ProficiencyProfile.
        """
        # Awareness: derived from trilemma score (0–100 → 0–1)
        profile.awareness.update(score.trilemma_score / 100)

        # Quality: derived from gricean score (0–100 → 0–1)
        profile.quality.update(score.gricean_score / 100)

        # Flexibility: derived from flexibility score (0–100 → 0–1)
        profile.flexibility.update(score.flexibility_score / 100)

        # Composure: only update if voice data present
        if score.composure_score is not None:
            profile.composure.update(score.composure_score / 100)

        return profile
