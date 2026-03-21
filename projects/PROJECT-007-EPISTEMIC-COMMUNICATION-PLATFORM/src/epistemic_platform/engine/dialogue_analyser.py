"""Dialogue analyser — post-session analysis of conversation quality.

Consumes the raw session data (messages, coaching_annotations, trilemma_state)
and produces a structured DialogueAnalysis that feeds the scoring rubric,
proficiency model, and growth tracker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GriceanProfile:
    """Aggregated Gricean maxim scores across all coaching annotations."""

    quantity: float = 0.0
    quality: float = 0.0
    relation: float = 0.0
    manner: float = 0.0
    sample_count: int = 0

    @property
    def average(self) -> float:
        scores = [self.quantity, self.quality, self.relation, self.manner]
        return sum(scores) / len(scores) if any(scores) else 0.0

    @property
    def improvement(self) -> float:
        """Not computable from aggregate alone — set externally."""
        return 0.0


@dataclass
class TrilemmaProfile:
    """Extracted trilemma navigation metrics."""

    horns_visited: int = 0
    horns_escaped: int = 0
    escape_rate: float = 0.0
    unique_horns: list[str] = field(default_factory=list)
    escape_strategies: list[str] = field(default_factory=list)


@dataclass
class StanceProfile:
    """Extracted stance detection metrics."""

    primary_stance: str | None = None
    unique_stances: list[str] = field(default_factory=list)
    stance_shift_detected: bool = False
    stance_diversity: int = 0


@dataclass
class DialogueAnalysis:
    """Complete post-session dialogue analysis.

    This is the canonical output consumed by:
    - scoring_rubric.py  → SessionScore
    - proficiency_model.py → 4-axis proficiency update
    - growth_tracker.py  → cross-session trend
    - milestone_detector.py → achievement checks
    """

    session_id: int
    user_id: int
    total_turns: int = 0
    coaching_count: int = 0

    # Gricean analysis
    gricean: GriceanProfile = field(default_factory=GriceanProfile)
    gricean_improvement: float = 0.0  # last coaching avg - first coaching avg

    # Trilemma analysis
    trilemma: TrilemmaProfile = field(default_factory=TrilemmaProfile)

    # Stance analysis
    stance: StanceProfile = field(default_factory=StanceProfile)

    # Composure (voice sessions only, None for text)
    avg_composure: float | None = None
    composure_improvement: float | None = None

    # Raw data refs for downstream consumers
    scenario_id: int | None = None
    actor_id: int | None = None
    difficulty: str = "beginner"

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "total_turns": self.total_turns,
            "coaching_count": self.coaching_count,
            "gricean": {
                "quantity": self.gricean.quantity,
                "quality": self.gricean.quality,
                "relation": self.gricean.relation,
                "manner": self.gricean.manner,
                "average": self.gricean.average,
                "sample_count": self.gricean.sample_count,
            },
            "gricean_improvement": self.gricean_improvement,
            "trilemma": {
                "horns_visited": self.trilemma.horns_visited,
                "horns_escaped": self.trilemma.horns_escaped,
                "escape_rate": self.trilemma.escape_rate,
                "unique_horns": self.trilemma.unique_horns,
                "escape_strategies": self.trilemma.escape_strategies,
            },
            "stance": {
                "primary_stance": self.stance.primary_stance,
                "unique_stances": self.stance.unique_stances,
                "stance_shift_detected": self.stance.stance_shift_detected,
                "stance_diversity": self.stance.stance_diversity,
            },
            "avg_composure": self.avg_composure,
            "composure_improvement": self.composure_improvement,
            "scenario_id": self.scenario_id,
            "actor_id": self.actor_id,
            "difficulty": self.difficulty,
        }


class DialogueAnalyser:
    """Analyses a completed conversation session to produce DialogueAnalysis."""

    def analyse(self, session_data: dict[str, Any]) -> DialogueAnalysis:
        """Analyse a completed session.

        Parameters
        ----------
        session_data : dict
            Must contain: id, user_id, messages, coaching_annotations,
            trilemma_state, turn_count, actor_id, scenario_id.
            Optionally: scenario.difficulty.

        Returns
        -------
        DialogueAnalysis with all metrics populated.
        """
        session_id = session_data["id"]
        user_id = session_data["user_id"]
        messages = session_data.get("messages", [])
        coaching = session_data.get("coaching_annotations", [])
        trilemma = session_data.get("trilemma_state", {})
        turn_count = session_data.get("turn_count", 0)
        outcome = trilemma.get("session_outcome", {})

        analysis = DialogueAnalysis(
            session_id=session_id,
            user_id=user_id,
            total_turns=turn_count,
            coaching_count=len(coaching),
            actor_id=session_data.get("actor_id"),
            scenario_id=session_data.get("scenario_id"),
            difficulty=session_data.get("difficulty", "beginner"),
        )

        # Gricean aggregation
        analysis.gricean = self._aggregate_gricean(coaching)
        analysis.gricean_improvement = self._compute_gricean_improvement(coaching)

        # Trilemma metrics
        analysis.trilemma = self._extract_trilemma(trilemma)

        # Stance metrics
        analysis.stance = self._extract_stance(trilemma, outcome)

        # Composure from voice sessions
        composure_data = self._extract_composure(messages, outcome)
        analysis.avg_composure = composure_data.get("avg_composure")
        analysis.composure_improvement = composure_data.get("composure_improvement")

        return analysis

    def _aggregate_gricean(self, coaching: list[dict]) -> GriceanProfile:
        """Average Gricean scores across all coaching annotations."""
        if not coaching:
            return GriceanProfile()

        totals: dict[str, float] = {"quantity": 0, "quality": 0, "relation": 0, "manner": 0}
        count = 0

        for ann in coaching:
            scores = ann.get("gricean_scores", {})
            if scores:
                count += 1
                for key in totals:
                    totals[key] += float(scores.get(key, 0))

        if count == 0:
            return GriceanProfile()

        return GriceanProfile(
            quantity=round(totals["quantity"] / count, 1),
            quality=round(totals["quality"] / count, 1),
            relation=round(totals["relation"] / count, 1),
            manner=round(totals["manner"] / count, 1),
            sample_count=count,
        )

    def _compute_gricean_improvement(self, coaching: list[dict]) -> float:
        """Compute improvement from first to last coaching annotation."""
        scored = [a for a in coaching if a.get("gricean_scores")]
        if len(scored) < 2:
            return 0.0

        first = scored[0]["gricean_scores"]
        last = scored[-1]["gricean_scores"]
        first_avg = sum(float(v) for v in first.values()) / max(len(first), 1)
        last_avg = sum(float(v) for v in last.values()) / max(len(last), 1)
        return round(last_avg - first_avg, 1)

    def _extract_trilemma(self, trilemma: dict) -> TrilemmaProfile:
        """Extract trilemma navigation metrics from trilemma_state."""
        horn_visits = trilemma.get("horn_visits", [])
        total = len(horn_visits)
        escaped = sum(1 for v in horn_visits if v.get("escaped"))
        unique = list({v.get("horn", "") for v in horn_visits if v.get("horn")})
        strategies = [
            v.get("escape_strategy", "")
            for v in horn_visits
            if v.get("escaped") and v.get("escape_strategy")
        ]

        return TrilemmaProfile(
            horns_visited=total,
            horns_escaped=escaped,
            escape_rate=round(escaped / total, 2) if total > 0 else 0.0,
            unique_horns=unique,
            escape_strategies=strategies,
        )

    def _extract_stance(self, trilemma: dict, outcome: dict) -> StanceProfile:
        """Extract stance metrics from trilemma_state and session_outcome."""
        stance_history = trilemma.get("stance_history", [])
        unique = list({s.get("stance", "") for s in stance_history if s.get("stance")})

        primary = None
        if stance_history:
            # Most recent stance
            primary = stance_history[-1].get("stance")

        return StanceProfile(
            primary_stance=primary,
            unique_stances=unique,
            stance_shift_detected=outcome.get("stance_shift_detected", len(unique) > 1),
            stance_diversity=len(unique),
        )

    def _extract_composure(self, messages: list[dict], outcome: dict) -> dict:
        """Extract composure metrics from voice session messages."""
        # Check outcome first (already computed by end_session)
        if outcome.get("avg_composure") is not None:
            return {
                "avg_composure": outcome.get("avg_composure"),
                "composure_improvement": outcome.get("composure_improvement"),
            }

        # Fall back to computing from message vocal_state data
        composure_scores = []
        for msg in messages:
            vocal = msg.get("vocal_state")
            if vocal and "composure_score" in vocal:
                composure_scores.append(float(vocal["composure_score"]))

        if not composure_scores:
            return {"avg_composure": None, "composure_improvement": None}

        avg = sum(composure_scores) / len(composure_scores)
        improvement = 0.0
        if len(composure_scores) >= 4:
            mid = len(composure_scores) // 2
            first_half = sum(composure_scores[:mid]) / mid
            second_half = sum(composure_scores[mid:]) / (len(composure_scores) - mid)
            improvement = second_half - first_half

        return {
            "avg_composure": round(avg, 2),
            "composure_improvement": round(improvement, 2),
        }
