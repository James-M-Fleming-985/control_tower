"""ConversationSession Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ConversationSessionCreate(BaseModel):
    actor_id: int
    scenario_id: int | None = None
    mode: str = "text"


class ConversationSessionUpdate(BaseModel):
    status: str | None = None
    mode: str | None = None
    ended_at: datetime | None = None


class ConversationSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    actor_id: int
    scenario_id: int | None
    status: str
    mode: str
    messages: list[dict[str, Any]]
    coaching_annotations: list[dict[str, Any]]
    trilemma_state: dict[str, Any]
    turn_count: int
    started_at: datetime
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ConversationSessionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int
    status: str
    mode: str
    turn_count: int
    started_at: datetime
    ended_at: datetime | None
