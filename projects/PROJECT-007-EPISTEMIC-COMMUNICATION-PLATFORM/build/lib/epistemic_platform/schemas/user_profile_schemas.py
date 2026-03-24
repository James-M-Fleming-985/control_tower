"""UserProfile Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr


class UserProfileBase(BaseModel):
    email: str
    display_name: str
    skill_level: str = "beginner"
    preferences: dict[str, Any] = {}


class UserProfileCreate(UserProfileBase):
    password: str


class UserProfileUpdate(BaseModel):
    display_name: str | None = None
    skill_level: str | None = None
    preferences: dict[str, Any] | None = None


class UserProfileRead(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assessment_history: list[dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
