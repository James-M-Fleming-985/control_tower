"""Actor evolution — adapts actor behaviour based on aggregated user feedback.

Analyses how actors perform across sessions and suggests parameter adjustments:
- Actors that are too easy/hard based on average scores
- Actors that produce the most stance shifts
- Actor effectiveness at triggering trilemma navigation
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActorPerformance:
    """Performance metrics for a single actor across sessions."""

    actor_id: int
    actor_name: str = ""
    total_sessions: int = 0
    average_score: float = 0.0
    average_gricean: float = 0.0
    average_trilemma: float = 0.0
    stance_shift_rate: float = 0.0  # % of sessions with stance shift
    horn_escape_rate: float = 0.0   # average escape rate
    difficulty_suggestion: str = ""  # "increase", "decrease", or "maintain"

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "actor_name": self.actor_name,
            "total_sessions": self.total_sessions,
            "average_score": round(self.average_score, 1),
            "average_gricean": round(self.average_gricean, 1),
            "average_trilemma": round(self.average_trilemma, 1),
            "stance_shift_rate": round(self.stance_shift_rate, 2),
            "horn_escape_rate": round(self.horn_escape_rate, 2),
            "difficulty_suggestion": self.difficulty_suggestion,
        }


@dataclass
class EvolutionReport:
    """Actor evolution analysis across all actors."""

    actors: list[ActorPerformance] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "actors": [a.to_dict() for a in self.actors],
        }


class ActorEvolution:
    """Analyses actor performance and suggests adjustments."""

    def analyse(
        self,
        sessions_data: list[dict[str, Any]],
        actors: dict[int, str],
    ) -> EvolutionReport:
        """Compute actor performance from session data.

        Parameters
        ----------
        sessions_data : list[dict]
            Each dict must have actor_id, plus session_outcome or scoring data.
        actors : dict[int, str]
            Mapping of actor_id → actor_name.
        """
        # Group by actor
        by_actor: dict[int, list[dict]] = defaultdict(list)
        for sd in sessions_data:
            aid = sd.get("actor_id")
            if aid is not None:
                by_actor[aid].append(sd)

        report = EvolutionReport()

        for actor_id, sessions in by_actor.items():
            perf = self._compute_actor_performance(
                actor_id, actors.get(actor_id, f"Actor {actor_id}"), sessions
            )
            report.actors.append(perf)

        # Sort by session count descending
        report.actors.sort(key=lambda a: a.total_sessions, reverse=True)
        return report

    def _compute_actor_performance(
        self, actor_id: int, name: str, sessions: list[dict]
    ) -> ActorPerformance:
        n = len(sessions)
        perf = ActorPerformance(actor_id=actor_id, actor_name=name, total_sessions=n)

        if n == 0:
            return perf

        total_score = 0.0
        total_gricean = 0.0
        total_trilemma = 0.0
        stance_shifts = 0
        escape_rates = []

        for sd in sessions:
            outcome = sd.get("trilemma_state", {}).get("session_outcome", {})

            total_score += outcome.get("final_score", 0)
            total_gricean += outcome.get("gricean_score", 0)
            total_trilemma += outcome.get("trilemma_navigation_score", 0) * 100

            if outcome.get("stance_shift_detected"):
                stance_shifts += 1

            horns = outcome.get("horns_visited", 0)
            escaped = outcome.get("horns_escaped", 0)
            if horns > 0:
                escape_rates.append(escaped / horns)

        perf.average_score = total_score / n
        perf.average_gricean = total_gricean / n
        perf.average_trilemma = total_trilemma / n
        perf.stance_shift_rate = stance_shifts / n
        perf.horn_escape_rate = (
            sum(escape_rates) / len(escape_rates) if escape_rates else 0.0
        )

        # Difficulty suggestion
        if perf.average_score > 85:
            perf.difficulty_suggestion = "increase"
        elif perf.average_score < 45:
            perf.difficulty_suggestion = "decrease"
        else:
            perf.difficulty_suggestion = "maintain"

        return perf
