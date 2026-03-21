"""XP system — experience point awards and level progression.

Awards XP based on session performance and milestones.
Computes level from cumulative XP using a curve.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from epistemic_platform.engine.milestone_detector import MilestoneResult
from epistemic_platform.engine.scoring_rubric import SessionScore

# ── Level curve ──────────────────────────────────────────────────────
# XP required for each level: level_xp(n) = 100 * n^1.5
# Level 1 = 0 XP, Level 2 = 100, Level 3 = 283, Level 4 = 520, ...


def xp_for_level(level: int) -> int:
    """Total cumulative XP required to reach this level."""
    if level <= 1:
        return 0
    return int(100 * (level - 1) ** 1.5)


def level_from_xp(total_xp: int) -> int:
    """Compute level from cumulative XP."""
    level = 1
    while xp_for_level(level + 1) <= total_xp:
        level += 1
    return level


# ── Base XP awards ───────────────────────────────────────────────────
# Grade → base XP for completing a session
_GRADE_XP: dict[str, int] = {
    "S": 120,
    "A": 100,
    "B": 80,
    "C": 60,
    "D": 40,
}


@dataclass
class XPAward:
    """Breakdown of XP awarded for a session."""

    session_base: int = 0        # Grade-based base XP
    milestone_bonus: int = 0     # Sum of milestone XP rewards
    improvement_bonus: int = 0   # Bonus for improving over previous session
    total: int = 0
    new_level: int = 0           # Level after this award
    levelled_up: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_base": self.session_base,
            "milestone_bonus": self.milestone_bonus,
            "improvement_bonus": self.improvement_bonus,
            "total": self.total,
            "new_level": self.new_level,
            "levelled_up": self.levelled_up,
        }


class XPSystem:
    """Computes XP awards and level progression."""

    def award(
        self,
        score: SessionScore,
        milestones: MilestoneResult,
        current_xp: int,
        current_level: int,
        previous_score: float | None = None,
    ) -> XPAward:
        """Compute XP award for a completed session.

        Parameters
        ----------
        score : SessionScore
        milestones : MilestoneResult
        current_xp : int
            User's XP before this session.
        current_level : int
            User's level before this session.
        previous_score : float or None
            Final score from the user's previous session (for improvement bonus).
        """
        award = XPAward()

        # Base XP from grade
        award.session_base = _GRADE_XP.get(score.grade, 40)

        # Milestone bonus
        award.milestone_bonus = sum(m.xp_reward for m in milestones.newly_unlocked)

        # Improvement bonus: +25 XP if score improved by 5+ over previous
        if previous_score is not None and score.final_score >= previous_score + 5:
            award.improvement_bonus = 25

        award.total = award.session_base + award.milestone_bonus + award.improvement_bonus

        # Level check
        new_total_xp = current_xp + award.total
        award.new_level = level_from_xp(new_total_xp)
        award.levelled_up = award.new_level > current_level

        return award
