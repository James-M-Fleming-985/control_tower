from __future__ import annotations

"""ScenarioDefinition router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.auth.dependencies import get_current_user
from epistemic_platform.database import get_db
from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.repositories.scenario_definition_repository import (
    ScenarioDefinitionRepository,
)
from epistemic_platform.schemas.scenario_definition_schemas import (
    ScenarioDefinitionCreate,
    ScenarioDefinitionRead,
    ScenarioDefinitionUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[ScenarioDefinitionRead])
async def list_scenarios(
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    difficulty: str | None = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ScenarioDefinitionRepository(db)
    return await repo.list(
        skip=skip, limit=limit, category=category, difficulty=difficulty, active_only=active_only
    )


@router.get("/{scenario_id}", response_model=ScenarioDefinitionRead)
async def get_scenario(
    scenario_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ScenarioDefinitionRepository(db)
    scenario = await repo.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return scenario


@router.post("/", response_model=ScenarioDefinitionRead, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    data: ScenarioDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ScenarioDefinitionRepository(db)
    return await repo.create(data)


@router.patch("/{scenario_id}", response_model=ScenarioDefinitionRead)
async def update_scenario(
    scenario_id: int,
    data: ScenarioDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ScenarioDefinitionRepository(db)
    scenario = await repo.update(scenario_id, data)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return scenario


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ScenarioDefinitionRepository(db)
    deleted = await repo.delete(scenario_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
