"""Milestone detector — evaluates predefined milestones after each session.

Milestones are checked against the DialogueAnalysis, SessionScore, and
GrowthReport to determine which achievements have been unlocked.
Feeds into the achievement_engine for XP and badge grants.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from epistemic_platform.engine.dialogue_analyser import DialogueAnalysis
from epistemic_platform.engine.growth_tracker import GrowthReport
from epistemic_platform.engine.scoring_rubric import SessionScore


class MilestoneCategory(str, Enum):
    SESSION = "session"        # Single-session achievements
    GROWTH = "growth"          # Cross-session progression
    MASTERY = "mastery"        # Skill mastery thresholds
    EXPLORATION = "exploration" # Breadth of engagement


@dataclass
class MilestoneDefinition:
    """A predefined milestone that can be unlocked."""

    id: str
    name: str
    description: str
    category: MilestoneCategory
    icon: str = ""
    xp_reward: int = 0
    check: Callable[..., bool] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "icon": self.icon,
            "xp_reward": self.xp_reward,
        }


@dataclass
class MilestoneResult:
    """Result of checking milestones after a session."""

    newly_unlocked: list[MilestoneDefinition]
    total_checked: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "newly_unlocked": [m.to_dict() for m in self.newly_unlocked],
            "total_checked": self.total_checked,
        }


# ── Milestone check functions ────────────────────────────────────────

def _first_session(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return g is not None and g.total_sessions >= 1

def _five_sessions(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return g is not None and g.total_sessions >= 5

def _ten_sessions(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return g is not None and g.total_sessions >= 10

def _first_horn_escape(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return a.trilemma.horns_escaped >= 1

def _escape_all_horns(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return len(a.trilemma.unique_horns) >= 3 and a.trilemma.escape_rate >= 0.5

def _stance_explorer(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return g is not None and len(g.all_stances_encountered) >= 4

def _stance_master(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return g is not None and len(g.all_stances_encountered) >= 7

def _gricean_ace(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return s.gricean_score >= 85

def _s_rank(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return s.grade == "S"

def _a_streak_3(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return g is not None and g.sessions_above_b >= 3

def _a_streak_5(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return g is not None and g.sessions_above_b >= 5

def _composure_master(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return s.composure_score is not None and s.composure_score >= 85

def _improvement_arc(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return g is not None and g.score_improvement >= 15

def _deep_engagement(a: DialogueAnalysis, s: SessionScore, g: GrowthReport | None) -> bool:
    return a.total_turns >= 12 and a.coaching_count >= 3


# ── Milestone registry ───────────────────────────────────────────────

MILESTONES: list[MilestoneDefinition] = [
    # Session milestones
    MilestoneDefinition("first_session", "First Steps", "Complete your first session", MilestoneCategory.SESSION, "🎯", 50, _first_session),
    MilestoneDefinition("first_escape", "Horn Breaker", "Escape a trilemma horn for the first time", MilestoneCategory.SESSION, "🔓", 75, _first_horn_escape),
    MilestoneDefinition("escape_all_horns", "Trilemma Navigator", "Encounter and escape all 3 horns in one session", MilestoneCategory.SESSION, "🧭", 150, _escape_all_horns),
    MilestoneDefinition("gricean_ace", "Communication Ace", "Score 85+ on Gricean quality", MilestoneCategory.SESSION, "💬", 100, _gricean_ace),
    MilestoneDefinition("s_rank", "S-Rank", "Achieve an S-rank session score", MilestoneCategory.SESSION, "⭐", 200, _s_rank),
    MilestoneDefinition("deep_engagement", "Deep Dive", "12+ turns with 3+ coaching rounds", MilestoneCategory.SESSION, "🌊", 100, _deep_engagement),
    MilestoneDefinition("composure_master", "Calm Under Pressure", "Score 85+ composure in a voice session", MilestoneCategory.SESSION, "🧘", 125, _composure_master),

    # Growth milestones
    MilestoneDefinition("five_sessions", "Regular Practitioner", "Complete 5 sessions", MilestoneCategory.GROWTH, "📚", 100, _five_sessions),
    MilestoneDefinition("ten_sessions", "Dedicated Learner", "Complete 10 sessions", MilestoneCategory.GROWTH, "🎓", 200, _ten_sessions),
    MilestoneDefinition("improvement_arc", "Growth Mindset", "Improve your average score by 15+ points", MilestoneCategory.GROWTH, "📈", 150, _improvement_arc),
    MilestoneDefinition("a_streak_3", "Consistency", "3 consecutive B+ sessions", MilestoneCategory.GROWTH, "🔥", 125, _a_streak_3),
    MilestoneDefinition("a_streak_5", "On Fire", "5 consecutive B+ sessions", MilestoneCategory.GROWTH, "🔥🔥", 200, _a_streak_5),

    # Exploration milestones
    MilestoneDefinition("stance_explorer", "Stance Explorer", "Encounter 4+ different stances", MilestoneCategory.EXPLORATION, "🗺️", 100, _stance_explorer),
    MilestoneDefinition("stance_master", "Epistemological Polyglot", "Encounter 7+ different stances", MilestoneCategory.EXPLORATION, "🌍", 250, _stance_master),
]

MILESTONE_REGISTRY: dict[str, MilestoneDefinition] = {m.id: m for m in MILESTONES}


class MilestoneDetector:
    """Evaluates milestones against session data."""

    def check(
        self,
        analysis: DialogueAnalysis,
        score: SessionScore,
        growth: GrowthReport | None,
        already_unlocked: set[str],
    ) -> MilestoneResult:
        """Check all milestones, returning newly unlocked ones.

        Parameters
        ----------
        analysis : DialogueAnalysis
            Current session analysis.
        score : SessionScore
            Current session score.
        growth : GrowthReport or None
            Cross-session growth report (None if first session).
        already_unlocked : set[str]
            Set of milestone IDs the user has already earned.

        Returns
        -------
        MilestoneResult with newly unlocked milestones.
        """
        newly_unlocked = []

        for milestone in MILESTONES:
            if milestone.id in already_unlocked:
                continue
            if milestone.check is None:
                continue
            if milestone.check(analysis, score, growth):
                newly_unlocked.append(milestone)

        return MilestoneResult(
            newly_unlocked=newly_unlocked,
            total_checked=len(MILESTONES),
        )
