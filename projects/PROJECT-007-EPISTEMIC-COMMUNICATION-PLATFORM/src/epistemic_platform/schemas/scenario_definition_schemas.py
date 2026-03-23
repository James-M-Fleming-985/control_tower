"""ScenarioDefinition Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ScenarioDefinitionBase(BaseModel):
    title: str
    description: str | None = None
    difficulty: str
    actor_id: int | None = None
    objectives: list[Any] = []
    evaluation_criteria: list[Any] = []
    category: str
    is_active: bool = True


class ScenarioDefinitionCreate(ScenarioDefinitionBase):
    pass


class ScenarioDefinitionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    difficulty: str | None = None
    actor_id: int | None = None
    objectives: list[Any] | None = None
    evaluation_criteria: list[Any] | None = None
    category: str | None = None
    is_active: bool | None = None


class ScenarioDefinitionRead(ScenarioDefinitionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
