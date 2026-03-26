"""Scoring rubric — converts DialogueAnalysis into a weighted SessionScore.

Five scoring dimensions:
1. Gricean Quality   (communication adherence)
2. Trilemma Navigation (horn escape rate)
3. Stance Flexibility  (diversity of epistemological engagement)
4. Engagement Depth    (turn count + coaching utilisation)
5. Composure          (voice sessions only, optional)

Each dimension produces a 0–100 score.  The final weighted score is
multiplied by a difficulty factor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from epistemic_platform.engine.dialogue_analyser import DialogueAnalysis

# ── Difficulty multipliers ───────────────────────────────────────────

DIFFICULTY_MULTIPLIER: dict[str, float] = {
    "beginner": 1.0,
    "intermediate": 1.25,
    "advanced": 1.5,
    "expert": 1.75,
}


@dataclass
class SessionScore:
    """Weighted composite score for a single session."""

    gricean_score: float = 0.0         # 0–100
    trilemma_score: float = 0.0        # 0–100
    flexibility_score: float = 0.0     # 0–100
    engagement_score: float = 0.0      # 0–100
    composure_score: float | None = None  # 0–100 (voice only)

    raw_total: float = 0.0             # weighted sum before difficulty
    difficulty_multiplier: float = 1.0
    final_score: float = 0.0           # raw_total × difficulty_multiplier
    grade: str = ""                    # S / A / B / C / D

    def to_dict(self) -> dict[str, Any]:
        return {
            "gricean_score": round(self.gricean_score, 1),
            "trilemma_score": round(self.trilemma_score, 1),
            "flexibility_score": round(self.flexibility_score, 1),
            "engagement_score": round(self.engagement_score, 1),
            "composure_score": round(self.composure_score, 1) if self.composure_score is not None else None,
            "raw_total": round(self.raw_total, 1),
            "difficulty_multiplier": self.difficulty_multiplier,
            "final_score": round(self.final_score, 1),
            "grade": self.grade,
        }


# ── Weights ──────────────────────────────────────────────────────────
# Text sessions: 4 dimensions
_TEXT_WEIGHTS = {
    "gricean": 0.35,
    "trilemma": 0.30,
    "flexibility": 0.20,
    "engagement": 0.15,
}
# Voice sessions: 5 dimensions (composure gets 0.10, others scale down)
_VOICE_WEIGHTS = {
    "gricean": 0.30,
    "trilemma": 0.25,
    "flexibility": 0.17,
    "engagement": 0.13,
    "composure": 0.15,
}


def _grade(score: float) -> str:
    """Assign a letter grade from final score."""
    if score >= 95:
        return "S"
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    return "D"


class ScoringRubric:
    """Converts a DialogueAnalysis into a SessionScore."""

    def score(self, analysis: DialogueAnalysis) -> SessionScore:
        """Compute session score from analysis."""
        s = SessionScore()

        # 1. Gricean: average maxim score, scaled to 0–100 (raw is 1–10)
        s.gricean_score = min(analysis.gricean.average * 10, 100.0)

        # 2. Trilemma: blend escape rate with engagement credit
        #    Visiting horns shows awareness even without escaping them.
        horns_visited = len(analysis.trilemma.unique_horns)
        escape_component = analysis.trilemma.escape_rate * 100  # 0-100
        engagement_component = min(horns_visited * 20, 60)  # up to 60 for 3+ horns
        # 60% escape, 40% engagement — floor at 15 when any horn visited
        if horns_visited > 0:
            raw_trilemma = escape_component * 0.6 + engagement_component * 0.4
            s.trilemma_score = min(max(raw_trilemma, 15.0), 100.0)
        else:
            s.trilemma_score = 0.0

        # 3. Flexibility: stance diversity → 0–100
        #    1 stance = 25, 2 = 50, 3 = 75, 4+ = 100
        diversity = analysis.stance.stance_diversity
        s.flexibility_score = min(diversity * 25, 100.0)
        # Bonus for stance shift
        if analysis.stance.stance_shift_detected:
            s.flexibility_score = min(s.flexibility_score + 15, 100.0)

        # 4. Engagement: turn depth + coaching utilisation
        #    Ideal: 8+ turns with at least 2 coaching rounds
        turn_score = min(analysis.total_turns / 8 * 60, 60.0)
        coaching_score = min(analysis.coaching_count / 2 * 40, 40.0)
        s.engagement_score = min(turn_score + coaching_score, 100.0)

        # 5. Composure (voice only)
        has_composure = analysis.avg_composure is not None
        if has_composure:
            s.composure_score = min(analysis.avg_composure * 100, 100.0)
            # Bonus for improvement
            if analysis.composure_improvement and analysis.composure_improvement > 0:
                s.composure_score = min(
                    s.composure_score + analysis.composure_improvement * 50, 100.0
                )

        # Weighted total
        weights = _VOICE_WEIGHTS if has_composure else _TEXT_WEIGHTS
        s.raw_total = (
            s.gricean_score * weights["gricean"]
            + s.trilemma_score * weights["trilemma"]
            + s.flexibility_score * weights["flexibility"]
            + s.engagement_score * weights["engagement"]
        )
        if has_composure and s.composure_score is not None:
            s.raw_total += s.composure_score * weights["composure"]

        # Difficulty multiplier
        s.difficulty_multiplier = DIFFICULTY_MULTIPLIER.get(
            analysis.difficulty, 1.0
        )
        s.final_score = min(s.raw_total * s.difficulty_multiplier, 100.0)
        s.grade = _grade(s.final_score)

        return s
