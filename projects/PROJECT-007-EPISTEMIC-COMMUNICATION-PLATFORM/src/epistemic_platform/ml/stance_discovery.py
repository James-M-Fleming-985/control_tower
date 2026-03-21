"""Stance discovery — identifies emerging stance patterns across users.

Analyses aggregated stance data from completed sessions to discover:
- Most common stance transitions
- Stance clusters (users who share similar epistemological journeys)
- Emerging stances not yet in the ontology
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StanceTransition:
    """A transition between two stances observed across sessions."""

    from_stance: str
    to_stance: str
    count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_stance": self.from_stance,
            "to_stance": self.to_stance,
            "count": self.count,
        }


@dataclass
class StanceInsights:
    """Aggregated stance pattern insights."""

    total_sessions_analysed: int = 0
    most_common_stances: list[tuple[str, int]] = field(default_factory=list)
    most_common_transitions: list[StanceTransition] = field(default_factory=list)
    stance_distribution: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_sessions_analysed": self.total_sessions_analysed,
            "most_common_stances": [
                {"stance": s, "count": c} for s, c in self.most_common_stances
            ],
            "most_common_transitions": [t.to_dict() for t in self.most_common_transitions],
            "stance_distribution": self.stance_distribution,
        }


class StanceDiscovery:
    """Analyses stance patterns from aggregated session data."""

    def analyse(self, sessions_data: list[dict[str, Any]]) -> StanceInsights:
        """Compute stance insights from completed session data.

        Parameters
        ----------
        sessions_data : list[dict]
            Each dict should have trilemma_state with stance_history.
        """
        insights = StanceInsights(total_sessions_analysed=len(sessions_data))

        all_stances: list[str] = []
        transitions: list[tuple[str, str]] = []

        for sd in sessions_data:
            trilemma = sd.get("trilemma_state", {})
            stance_history = trilemma.get("stance_history", [])

            stances_in_session = [
                s.get("stance") for s in stance_history if s.get("stance")
            ]
            all_stances.extend(stances_in_session)

            # Extract transitions within a session
            for i in range(len(stances_in_session) - 1):
                if stances_in_session[i] != stances_in_session[i + 1]:
                    transitions.append(
                        (stances_in_session[i], stances_in_session[i + 1])
                    )

        # Most common stances
        stance_counts = Counter(all_stances)
        insights.most_common_stances = stance_counts.most_common(10)

        # Distribution
        total = sum(stance_counts.values())
        if total > 0:
            insights.stance_distribution = {
                s: round(c / total, 3) for s, c in stance_counts.items()
            }

        # Most common transitions
        transition_counts = Counter(transitions)
        insights.most_common_transitions = [
            StanceTransition(from_stance=t[0], to_stance=t[1], count=c)
            for t, c in transition_counts.most_common(10)
        ]

        return insights
