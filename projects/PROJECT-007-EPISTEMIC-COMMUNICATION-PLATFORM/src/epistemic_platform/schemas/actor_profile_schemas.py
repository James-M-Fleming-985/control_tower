"""ActorProfile Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ActorProfileBase(BaseModel):
    name: str
    description: str | None = None
    epistemological_stance: str
    ontology_config: dict[str, Any] = {}
    archetype: str | None = None
    is_active: bool = True
    avatar_config: dict[str, Any] | None = None


class ActorProfileCreate(ActorProfileBase):
    pass


class ActorProfileUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    epistemological_stance: str | None = None
    ontology_config: dict[str, Any] | None = None
    archetype: str | None = None
    is_active: bool | None = None
    avatar_config: dict[str, Any] | None = None


class ActorProfileRead(ActorProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
