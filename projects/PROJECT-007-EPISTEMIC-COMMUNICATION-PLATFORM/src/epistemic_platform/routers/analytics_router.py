"""Analytics router — platform-wide analytics and ML insights.

GET  /api/analytics/session/{id}    — single session analysis + score
GET  /api/analytics/stance-insights — aggregated stance patterns (admin)
GET  /api/analytics/actor-evolution  — actor performance + tuning suggestions (admin)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.auth.dependencies import get_current_user
from epistemic_platform.database import get_db
from epistemic_platform.engine.dialogue_analyser import DialogueAnalyser
from epistemic_platform.engine.scoring_rubric import ScoringRubric
from epistemic_platform.ml.actor_evolution import ActorEvolution
from epistemic_platform.ml.stance_discovery import StanceDiscovery
from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.repositories.actor_profile_repository import ActorProfileRepository
from epistemic_platform.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)

router = APIRouter()


@router.get("/session/{session_id}")
async def get_session_analytics(
    session_id: int,
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return analysis and score for a single completed session."""
    repo = ConversationSessionRepository(db)
    session = await repo.get(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your session")
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Session not yet completed")

    analyser = DialogueAnalyser()
    rubric = ScoringRubric()

    session_data = {
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

    analysis = analyser.analyse(session_data)
    score = rubric.score(analysis)

    return {
        "analysis": analysis.to_dict(),
        "score": score.to_dict(),
    }


@router.get("/stance-insights")
async def get_stance_insights(
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return aggregated stance pattern insights across all sessions."""
    repo = ConversationSessionRepository(db)
    sessions = await repo.list_completed_by_user(user.id)

    sessions_data = []
    for s in sessions:
        sessions_data.append({
            "trilemma_state": s.trilemma_state or {},
            "actor_id": s.actor_id,
        })

    discovery = StanceDiscovery()
    insights = discovery.analyse(sessions_data)
    return insights.to_dict()


@router.get("/actor-evolution")
async def get_actor_evolution(
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return actor performance analysis for the user's sessions."""
    repo = ConversationSessionRepository(db)
    sessions = await repo.list_completed_by_user(user.id)

    # Build actor name lookup
    actor_repo = ActorProfileRepository(db)
    actor_ids = {s.actor_id for s in sessions}
    actors = {}
    for aid in actor_ids:
        actor = await actor_repo.get(aid)
        if actor:
            actors[aid] = actor.name

    sessions_data = []
    for s in sessions:
        sessions_data.append({
            "actor_id": s.actor_id,
            "trilemma_state": s.trilemma_state or {},
        })

    evolution = ActorEvolution()
    report = evolution.analyse(sessions_data, actors)
    return report.to_dict()
