"""Session planner — generates conversation session plans.

Uses the user's AssessmentResult and proficiency profile to recommend
actors, scenarios, and focus areas for their next session.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from epistemic_platform.engine.assessment import AssessmentResult
from epistemic_platform.engine.proficiency_model import ProficiencyProfile


@dataclass
class SessionPlan:
    """A recommended session configuration."""

    recommended_actor_names: list[str] = field(default_factory=list)
    recommended_scenario_ids: list[int] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)
    difficulty: str = "beginner"
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommended_actor_names": self.recommended_actor_names,
            "recommended_scenario_ids": self.recommended_scenario_ids,
            "focus_areas": self.focus_areas,
            "difficulty": self.difficulty,
            "rationale": self.rationale,
        }


class SessionPlanner:
    """Plans next sessions based on assessment and proficiency data."""

    def plan(
        self,
        assessment: AssessmentResult | None = None,
        proficiency: ProficiencyProfile | None = None,
        completed_scenario_ids: list[int] | None = None,
    ) -> SessionPlan:
        """Generate a session plan.

        Parameters
        ----------
        assessment : AssessmentResult or None
            User's initial assessment (may be None for unassessed users).
        proficiency : ProficiencyProfile or None
            Current proficiency state.
        completed_scenario_ids : list[int] or None
            IDs of scenarios already completed by this user.
        """
        plan = SessionPlan()
        completed = set(completed_scenario_ids or [])

        # Use assessment recommendations if available
        if assessment:
            plan.recommended_actor_names = list(assessment.recommended_actors)
            plan.recommended_scenario_ids = [
                int(s) for s in assessment.recommended_scenarios
                if str(s).isdigit() and int(s) not in completed
            ]

        # Determine focus areas from proficiency weaknesses
        if proficiency:
            weaknesses = self._identify_weaknesses(proficiency)
            plan.focus_areas = weaknesses
            plan.difficulty = self._recommend_difficulty(proficiency)
            plan.rationale = self._build_rationale(weaknesses, proficiency)
        else:
            plan.focus_areas = ["general epistemological engagement"]
            plan.difficulty = "beginner"
            plan.rationale = "Starting session — explore at your own pace."

        return plan

    def _identify_weaknesses(self, prof: ProficiencyProfile) -> list[str]:
        """Identify the user's weakest axes for targeted practice."""
        axes = [
            ("awareness", prof.awareness.value, "trilemma navigation"),
            ("quality", prof.quality.value, "communication quality (Gricean maxims)"),
            ("flexibility", prof.flexibility.value, "stance flexibility"),
        ]
        if prof.composure.history:
            axes.append(("composure", prof.composure.value, "composure under pressure"))

        # Sort by value ascending — weakest first
        axes.sort(key=lambda x: x[1])

        # Return focus areas for axes below 0.6
        return [label for _, val, label in axes if val < 0.6] or [axes[0][2]]

    def _recommend_difficulty(self, prof: ProficiencyProfile) -> str:
        """Recommend difficulty based on overall proficiency."""
        overall = prof.overall
        if overall >= 0.75:
            return "expert"
        if overall >= 0.55:
            return "advanced"
        if overall >= 0.35:
            return "intermediate"
        return "beginner"

    def _build_rationale(self, weaknesses: list[str], prof: ProficiencyProfile) -> str:
        """Build a human-readable rationale for the session plan."""
        if not weaknesses:
            return "Well-rounded performance — continue challenging yourself."

        focus = ", ".join(weaknesses[:2])
        return (
            f"Focus on {focus}. "
            f"Overall proficiency: {prof.overall:.0%}."
        )
