from __future__ import annotations

"""UserProfile database model."""

from typing import Any

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from epistemic_platform.models.base import BaseModel


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    skill_level: Mapped[str] = mapped_column(String(50), default="beginner", nullable=False)
    assessment_history: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=list)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # M4: Gamification
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    achievements: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=list)
    subscription_tier: Mapped[str] = mapped_column(String(20), default="free", nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False, server_default="user")

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, email='{self.email}')>"
