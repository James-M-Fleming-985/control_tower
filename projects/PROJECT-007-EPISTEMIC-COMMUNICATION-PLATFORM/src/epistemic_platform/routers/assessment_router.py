"""Assessment router — pre-conversation epistemological profiling.

GET  /api/assessment/questions          — returns calibration questions
POST /api/assessment/evaluate           — takes answers, returns assessment result
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from epistemic_platform.auth.dependencies import get_current_user
from epistemic_platform.database import get_db
from epistemic_platform.engine.assessment import AssessmentEngine
from epistemic_platform.engine.syllabus_engine import SyllabusEngine
from epistemic_platform.llm.claude_adapter import ClaudeCoachingAdapter
from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.repositories.actor_profile_repository import ActorProfileRepository
from epistemic_platform.repositories.scenario_definition_repository import ScenarioDefinitionRepository

router = APIRouter()


class AssessmentAnswers(BaseModel):
    answers: dict[str, str]  # {"q1": "a", "q2": "c", ...}


@router.get("/questions")
async def get_questions():
    """Return the calibration questions with options."""
    return {"questions": AssessmentEngine.get_questions()}


@router.post("/evaluate")
async def evaluate_assessment(
    body: AssessmentAnswers,
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Evaluate assessment answers and return epistemological profile."""
    coaching_llm = ClaudeCoachingAdapter()
    engine = AssessmentEngine(coaching_llm)
    result = await engine.evaluate(body.answers)

    # Persist result to user's assessment_history
    result_dict = result.to_dict()
    result_dict["completed_at"] = datetime.now(timezone.utc).isoformat()
    history = list(user.assessment_history or [])
    history.append(result_dict)
    user.assessment_history = history

    # Generate syllabus from assessment result
    scenario_repo = ScenarioDefinitionRepository(db)
    actor_repo = ActorProfileRepository(db)
    scenarios = await scenario_repo.list(active_only=True)
    actors = await actor_repo.list(active_only=True)

    scenario_dicts = [
        {
            "id": s.id,
            "title": s.title,
            "difficulty": s.difficulty,
            "category": s.category,
            "is_active": s.is_active,
        }
        for s in scenarios
    ]
    actor_ids = [a.id for a in actors]

    syllabus_engine = SyllabusEngine()
    syllabus = syllabus_engine.generate(
        assessment_result=result_dict,
        current_level=1,
        all_scenarios=scenario_dicts,
        all_actor_ids=actor_ids,
    )
    user.syllabus = syllabus

    # Reset legacy gamification (single user — clean slate)
    user.xp = 0
    user.level = 1
    user.achievements = []

    flag_modified(user, "assessment_history")
    flag_modified(user, "syllabus")
    db.add(user)
    await db.commit()

    return {**result_dict, "syllabus_generated": True}
