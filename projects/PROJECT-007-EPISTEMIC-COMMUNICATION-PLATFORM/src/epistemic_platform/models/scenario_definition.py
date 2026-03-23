from __future__ import annotations

"""ScenarioDefinition database model."""

from typing import Any

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from epistemic_platform.models.base import BaseModel


class ScenarioDefinition(BaseModel):
    __tablename__ = "scenario_definitions"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    actor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("actor_profiles.id"), nullable=True
    )
    objectives: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    evaluation_criteria: Mapped[list[Any]] = mapped_column(
        JSON, nullable=False, default=list
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<ScenarioDefinition(id={self.id}, title='{self.title}')>"
