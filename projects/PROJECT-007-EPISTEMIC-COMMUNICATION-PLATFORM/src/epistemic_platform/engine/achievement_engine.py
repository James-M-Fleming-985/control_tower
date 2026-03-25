"""Achievement engine — orchestrates post-session reward processing.

Ties together the dialogue analyser, scoring rubric, proficiency model,
growth tracker, milestone detector, and XP system into a single
post-session pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.engine.dialogue_analyser import DialogueAnalyser, DialogueAnalysis
from epistemic_platform.engine.growth_tracker import GrowthReport, GrowthTracker
from epistemic_platform.engine.milestone_detector import MilestoneDetector, MilestoneResult
from epistemic_platform.engine.proficiency_model import ProficiencyModel, ProficiencyProfile
from epistemic_platform.engine.scoring_rubric import ScoringRubric, SessionScore
from epistemic_platform.engine.xp_system import XPAward, XPSystem
from epistemic_platform.models.conversation_session import ConversationSession
from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class SessionReward:
    """Complete post-session reward package returned to the client."""

    analysis: DialogueAnalysis | None = None
    score: SessionScore | None = None
    growth: GrowthReport | None = None
    milestones: MilestoneResult | None = None
    xp_award: XPAward | None = None
    proficiency: ProficiencyProfile | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "score": self.score.to_dict() if self.score else None,
            "growth": self.growth.to_dict() if self.growth else None,
            "milestones": self.milestones.to_dict() if self.milestones else None,
            "xp_award": self.xp_award.to_dict() if self.xp_award else None,
            "proficiency": self.proficiency.to_dict() if self.proficiency else None,
        }


class AchievementEngine:
    """Processes a completed session through the full reward pipeline."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = ConversationSessionRepository(db)
        self._analyser = DialogueAnalyser()
        self._rubric = ScoringRubric()
        self._growth_tracker = GrowthTracker()
        self._proficiency_model = ProficiencyModel()
        self._milestone_detector = MilestoneDetector()
        self._xp_system = XPSystem()

    async def process_session(
        self,
        session: ConversationSession,
        user: UserProfile,
    ) -> SessionReward:
        """Run the full post-session reward pipeline.

        Parameters
        ----------
        session : ConversationSession
            The just-completed session (status should be 'completed').
        user : UserProfile
            The user who completed the session.

        Returns
        -------
        SessionReward with all computed rewards.
        """
        reward = SessionReward()

        # Idempotency: skip XP/milestone/proficiency persistence if already processed
        already_processed = bool(
            session.trilemma_state
            and isinstance(session.trilemma_state, dict)
            and session.trilemma_state.get("reward_processed")
        )
        if already_processed:
            logger.info("Session %d already reward-processed, returning read-only analysis", session.id)

        # 1. Analyse the session
        session_data = self._session_to_dict(session)
        reward.analysis = self._analyser.analyse(session_data)

        # 2. Score it
        reward.score = self._rubric.score(reward.analysis)

        # 3. Growth tracking — get all past completed sessions
        past_sessions = await self._repo.list_completed_by_user(user.id)
        # Exclude the current session if it's in the list
        past_sessions = [s for s in past_sessions if s.id != session.id]

        past_analyses = []
        past_scores = []
        for ps in past_sessions:
            pa = self._analyser.analyse(self._session_to_dict(ps))
            ps_score = self._rubric.score(pa)
            past_analyses.append(pa)
            past_scores.append(ps_score)

        # Add current session to the end
        all_analyses = past_analyses + [reward.analysis]
        all_scores = past_scores + [reward.score]

        reward.growth = self._growth_tracker.compute(
            user.id, all_analyses, all_scores
        )

        # 4. Milestones
        already_unlocked = set()
        if user.achievements:
            for ach in user.achievements:
                if isinstance(ach, dict) and "id" in ach:
                    already_unlocked.add(ach["id"])
                elif isinstance(ach, str):
                    already_unlocked.add(ach)

        reward.milestones = self._milestone_detector.check(
            reward.analysis, reward.score, reward.growth, already_unlocked
        )

        # 5. XP award
        previous_score = past_scores[-1].final_score if past_scores else None
        reward.xp_award = self._xp_system.award(
            reward.score,
            reward.milestones,
            current_xp=user.xp,
            current_level=user.level,
            previous_score=previous_score,
        )

        # 6. Proficiency model update
        prefs = user.preferences or {}
        proficiency_data = prefs.get("proficiency", {})
        profile = ProficiencyProfile.from_dict(proficiency_data)
        reward.proficiency = self._proficiency_model.update(
            profile, reward.analysis, reward.score
        )

        # 7. Persist user updates (skip if already processed to prevent double-award)
        if not already_processed:
            user.xp = user.xp + reward.xp_award.total
            user.level = reward.xp_award.new_level

            # Append newly unlocked milestones
            current_achievements = list(user.achievements) if user.achievements else []
            for m in reward.milestones.newly_unlocked:
                current_achievements.append(m.to_dict())
            user.achievements = current_achievements

            # Save proficiency in preferences
            prefs = dict(user.preferences) if user.preferences else {}
            prefs["proficiency"] = reward.proficiency.to_dict()
            user.preferences = prefs

            await self._db.flush()

            logger.info(
                "Session %d rewards: grade=%s, xp=+%d (→L%d), milestones=%d",
                session.id,
                reward.score.grade,
                reward.xp_award.total,
                reward.xp_award.new_level,
                len(reward.milestones.newly_unlocked),
            )

        return reward

    @staticmethod
    def _session_to_dict(session: ConversationSession) -> dict[str, Any]:
        """Convert a session ORM object to a dict for the analyser."""
        return {
            "id": session.id,
            "user_id": session.user_id,
            "actor_id": session.actor_id,
            "scenario_id": session.scenario_id,
            "messages": session.messages or [],
            "coaching_annotations": session.coaching_annotations or [],
            "trilemma_state": session.trilemma_state or {},
            "turn_count": session.turn_count,
            "difficulty": (
                session.scenario.difficulty
                if session.scenario and hasattr(session.scenario, "difficulty")
                else "beginner"
            ),
        }
