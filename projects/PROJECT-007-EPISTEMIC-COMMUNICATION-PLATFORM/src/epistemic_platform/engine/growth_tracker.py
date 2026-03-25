"""Growth tracker — cross-session trend analysis.

Analyses multiple completed sessions for a user to compute growth trends:
- Gricean improvement trajectory
- Trilemma navigation improvement
- Stance flexibility expansion
- Composure development (voice sessions)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from epistemic_platform.engine.dialogue_analyser import DialogueAnalysis
from epistemic_platform.engine.scoring_rubric import SessionScore


@dataclass
class TrendPoint:
    """A single data point in a growth trend."""

    session_id: int
    value: float
    label: str = ""


@dataclass
class GrowthReport:
    """Cross-session growth analysis for a user.

    Contains trend data and summary statistics across all completed sessions.
    """

    user_id: int
    total_sessions: int = 0
    total_turns: int = 0

    # Score trends (one per session, chronological)
    score_trend: list[TrendPoint] = field(default_factory=list)
    gricean_trend: list[TrendPoint] = field(default_factory=list)
    trilemma_trend: list[TrendPoint] = field(default_factory=list)
    flexibility_trend: list[TrendPoint] = field(default_factory=list)
    composure_trend: list[TrendPoint] = field(default_factory=list)

    # Summary stats
    average_score: float = 0.0
    best_score: float = 0.0
    score_improvement: float = 0.0  # last 3 avg - first 3 avg

    # Stance journey
    all_stances_encountered: list[str] = field(default_factory=list)
    stance_trend: list[dict[str, Any]] = field(default_factory=list)  # per-session primary stance

    # Streaks
    sessions_above_b: int = 0  # consecutive B+ sessions

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "total_sessions": self.total_sessions,
            "total_turns": self.total_turns,
            "score_trend": [
                {"session_id": p.session_id, "value": round(p.value, 1)}
                for p in self.score_trend
            ],
            "gricean_trend": [
                {"session_id": p.session_id, "value": round(p.value, 1)}
                for p in self.gricean_trend
            ],
            "trilemma_trend": [
                {"session_id": p.session_id, "value": round(p.value, 1)}
                for p in self.trilemma_trend
            ],
            "flexibility_trend": [
                {"session_id": p.session_id, "value": round(p.value, 1)}
                for p in self.flexibility_trend
            ],
            "composure_trend": [
                {"session_id": p.session_id, "value": round(p.value, 1)}
                for p in self.composure_trend
            ],
            "average_score": round(self.average_score, 1),
            "best_score": round(self.best_score, 1),
            "score_improvement": round(self.score_improvement, 1),
            "all_stances_encountered": self.all_stances_encountered,
            "stance_trend": self.stance_trend,
            "sessions_above_b": self.sessions_above_b,
        }


class GrowthTracker:
    """Computes cross-session growth from a list of analyses + scores."""

    def compute(
        self,
        user_id: int,
        analyses: list[DialogueAnalysis],
        scores: list[SessionScore],
    ) -> GrowthReport:
        """Compute growth report from chronologically ordered analyses/scores.

        Parameters
        ----------
        user_id : int
        analyses : list[DialogueAnalysis]
            Chronologically ordered (oldest first).
        scores : list[SessionScore]
            Parallel list — scores[i] corresponds to analyses[i].
        """
        n = len(analyses)
        report = GrowthReport(user_id=user_id, total_sessions=n)

        if n == 0:
            return report

        all_stances: set[str] = set()
        consecutive_b_plus = 0

        for i, (a, s) in enumerate(zip(analyses, scores)):
            sid = a.session_id
            report.total_turns += a.total_turns

            # Score trend
            report.score_trend.append(TrendPoint(session_id=sid, value=s.final_score))
            report.gricean_trend.append(TrendPoint(session_id=sid, value=s.gricean_score))
            report.trilemma_trend.append(TrendPoint(session_id=sid, value=s.trilemma_score))
            report.flexibility_trend.append(TrendPoint(session_id=sid, value=s.flexibility_score))

            if s.composure_score is not None:
                report.composure_trend.append(
                    TrendPoint(session_id=sid, value=s.composure_score)
                )

            # Stances
            all_stances.update(a.stance.unique_stances)
            if a.stance.primary_stance:
                report.stance_trend.append({
                    "session_id": sid,
                    "primary_stance": a.stance.primary_stance,
                    "unique_stances": a.stance.unique_stances,
                })

            # B+ streak
            if s.grade in ("S", "A", "B"):
                consecutive_b_plus += 1
            else:
                consecutive_b_plus = 0

        report.all_stances_encountered = sorted(all_stances)
        report.sessions_above_b = consecutive_b_plus

        # Summary stats
        final_scores = [p.value for p in report.score_trend]
        report.average_score = sum(final_scores) / n
        report.best_score = max(final_scores)

        # Improvement: avg of last 3 minus avg of first 3
        window = min(3, n)
        first_avg = sum(final_scores[:window]) / window
        last_avg = sum(final_scores[-window:]) / window
        report.score_improvement = last_avg - first_avg

        return report
