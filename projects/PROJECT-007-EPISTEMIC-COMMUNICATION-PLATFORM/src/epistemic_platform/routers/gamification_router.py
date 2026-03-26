"""Gamification router — user progress, XP, levels, achievements, proficiency.

GET  /api/gamification/profile      — user's gamification profile (xp, level, achievements)
GET  /api/gamification/proficiency   — 4-axis proficiency radar data
GET  /api/gamification/growth        — cross-session growth report
GET  /api/gamification/milestones    — all milestones with unlock status
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.auth.dependencies import get_current_user
from epistemic_platform.database import get_db
from epistemic_platform.engine.dialogue_analyser import DialogueAnalyser
from epistemic_platform.engine.growth_tracker import GrowthTracker
from epistemic_platform.engine.milestone_detector import MILESTONES
from epistemic_platform.engine.proficiency_model import ProficiencyModel, ProficiencyProfile
from epistemic_platform.engine.scoring_rubric import ScoringRubric
from epistemic_platform.engine.xp_system import level_from_xp, xp_for_level
from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)

router = APIRouter()


@router.get("/profile")
async def get_gamification_profile(
    user: UserProfile = Depends(get_current_user),
):
    """Return the user's gamification profile."""
    next_level = user.level + 1
    xp_current_level = xp_for_level(user.level)
    xp_next_level = xp_for_level(next_level)
    xp_progress = user.xp - xp_current_level
    xp_needed = xp_next_level - xp_current_level

    return {
        "xp": user.xp,
        "level": user.level,
        "xp_progress": xp_progress,
        "xp_needed": xp_needed,
        "achievements": user.achievements or [],
    }


@router.get("/proficiency")
async def get_proficiency(
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the user's 4-axis proficiency radar data.

    Reads cached proficiency from user.preferences.  If missing (e.g.
    preferences were overwritten), recomputes live from completed sessions.
    """
    prefs = user.preferences or {}
    proficiency_data = prefs.get("proficiency", {})

    # If proficiency data is present and non-empty, use it directly.
    if proficiency_data and any(
        proficiency_data.get(k, {}).get("value", 0) > 0
        for k in ("awareness", "quality", "flexibility", "composure")
    ):
        profile = ProficiencyProfile.from_dict(proficiency_data)
        return profile.to_dict()

    # Fallback: recompute from completed sessions.
    repo = ConversationSessionRepository(db)
    sessions = await repo.list_completed_by_user(user.id)

    analyser = DialogueAnalyser()
    rubric = ScoringRubric()
    model = ProficiencyModel()
    profile = ProficiencyProfile()

    for s in sessions:
        session_data = {
            "id": s.id,
            "user_id": s.user_id,
            "actor_id": s.actor_id,
            "scenario_id": s.scenario_id,
            "messages": s.messages or [],
            "coaching_annotations": s.coaching_annotations or [],
            "trilemma_state": s.trilemma_state or {},
            "turn_count": s.turn_count,
            "difficulty": (
                s.scenario.difficulty
                if s.scenario and hasattr(s.scenario, "difficulty")
                else "beginner"
            ),
        }
        a = analyser.analyse(session_data)
        sc = rubric.score(a)
        model.update(profile, a, sc)

    # Cache the recomputed proficiency back to preferences.
    if profile.overall > 0:
        new_prefs = dict(prefs)
        new_prefs["proficiency"] = profile.to_dict()
        user.preferences = new_prefs
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "preferences")
        await db.flush()

    return profile.to_dict()


@router.get("/growth")
async def get_growth_report(
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return cross-session growth report."""
    repo = ConversationSessionRepository(db)
    sessions = await repo.list_completed_by_user(user.id)

    analyser = DialogueAnalyser()
    rubric = ScoringRubric()
    tracker = GrowthTracker()

    analyses = []
    scores = []
    for s in sessions:
        session_data = {
            "id": s.id,
            "user_id": s.user_id,
            "actor_id": s.actor_id,
            "scenario_id": s.scenario_id,
            "messages": s.messages or [],
            "coaching_annotations": s.coaching_annotations or [],
            "trilemma_state": s.trilemma_state or {},
            "turn_count": s.turn_count,
            "difficulty": (
                s.scenario.difficulty
                if s.scenario and hasattr(s.scenario, "difficulty")
                else "beginner"
            ),
        }
        a = analyser.analyse(session_data)
        analyses.append(a)
        scores.append(rubric.score(a))

    report = tracker.compute(user.id, analyses, scores)
    return report.to_dict()


@router.get("/milestones")
async def get_milestones(
    user: UserProfile = Depends(get_current_user),
):
    """Return all milestones with unlock status."""
    unlocked_ids = set()
    if user.achievements:
        for ach in user.achievements:
            if isinstance(ach, dict) and "id" in ach:
                unlocked_ids.add(ach["id"])
            elif isinstance(ach, str):
                unlocked_ids.add(ach)

    result = []
    for m in MILESTONES:
        result.append({
            **m.to_dict(),
            "unlocked": m.id in unlocked_ids,
        })
    return {"milestones": result}
