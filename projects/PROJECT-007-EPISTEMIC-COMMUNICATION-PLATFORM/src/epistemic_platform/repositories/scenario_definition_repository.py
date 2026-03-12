from __future__ import annotations

"""ScenarioDefinition repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.models.scenario_definition import ScenarioDefinition
from epistemic_platform.schemas.scenario_definition_schemas import (
    ScenarioDefinitionCreate,
    ScenarioDefinitionUpdate,
)


class ScenarioDefinitionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, scenario_id: int) -> ScenarioDefinition | None:
        result = await self.db.execute(
            select(ScenarioDefinition).where(ScenarioDefinition.id == scenario_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        difficulty: str | None = None,
        active_only: bool = True,
    ) -> list[ScenarioDefinition]:
        query = select(ScenarioDefinition)
        if active_only:
            query = query.where(ScenarioDefinition.is_active.is_(True))
        if category:
            query = query.where(ScenarioDefinition.category == category)
        if difficulty:
            query = query.where(ScenarioDefinition.difficulty == difficulty)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, data: ScenarioDefinitionCreate) -> ScenarioDefinition:
        scenario = ScenarioDefinition(**data.model_dump())
        self.db.add(scenario)
        await self.db.flush()
        return scenario

    async def update(
        self, scenario_id: int, data: ScenarioDefinitionUpdate
    ) -> ScenarioDefinition | None:
        scenario = await self.get(scenario_id)
        if not scenario:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(scenario, field, value)
        await self.db.flush()
        return scenario

    async def delete(self, scenario_id: int) -> bool:
        scenario = await self.get(scenario_id)
        if not scenario:
            return False
        await self.db.delete(scenario)
        await self.db.flush()
        return True
