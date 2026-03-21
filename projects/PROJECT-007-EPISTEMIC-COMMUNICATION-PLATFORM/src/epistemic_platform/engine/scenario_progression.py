"""Scenario progression — gates scenarios by user level and completion.

Controls which scenarios are available to a user based on their level,
completed scenarios, and subscription tier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Level requirements by difficulty
DIFFICULTY_LEVEL_GATE: dict[str, int] = {
    "beginner": 1,
    "intermediate": 3,
    "advanced": 5,
    "expert": 8,
}


@dataclass
class ScenarioAccess:
    """Access status for a single scenario."""

    scenario_id: int
    title: str
    difficulty: str
    category: str
    available: bool
    reason: str = ""
    completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "title": self.title,
            "difficulty": self.difficulty,
            "category": self.category,
            "available": self.available,
            "reason": self.reason,
            "completed": self.completed,
        }


class ScenarioProgression:
    """Determines scenario availability based on user progression."""

    def evaluate(
        self,
        scenarios: list[dict[str, Any]],
        user_level: int,
        completed_scenario_ids: set[int],
    ) -> list[ScenarioAccess]:
        """Evaluate which scenarios are available to this user.

        Parameters
        ----------
        scenarios : list[dict]
            All scenario definitions (id, title, difficulty, category, is_active).
        user_level : int
            User's current level.
        completed_scenario_ids : set[int]
            IDs of scenarios the user has completed.

        Returns
        -------
        List of ScenarioAccess with availability status.
        """
        result = []

        for s in scenarios:
            if not s.get("is_active", True):
                continue

            sid = s["id"]
            difficulty = s.get("difficulty", "beginner")
            required_level = DIFFICULTY_LEVEL_GATE.get(difficulty, 1)
            completed = sid in completed_scenario_ids

            if user_level >= required_level:
                access = ScenarioAccess(
                    scenario_id=sid,
                    title=s["title"],
                    difficulty=difficulty,
                    category=s.get("category", ""),
                    available=True,
                    completed=completed,
                )
            else:
                access = ScenarioAccess(
                    scenario_id=sid,
                    title=s["title"],
                    difficulty=difficulty,
                    category=s.get("category", ""),
                    available=False,
                    reason=f"Requires level {required_level} (you are level {user_level})",
                    completed=False,
                )

            result.append(access)

        return result
