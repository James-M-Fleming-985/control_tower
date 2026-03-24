from __future__ import annotations

"""ActorProfile database model."""

from typing import Any

from sqlalchemy import Boolean, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from epistemic_platform.models.base import BaseModel


class ActorProfile(BaseModel):
    __tablename__ = "actor_profiles"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    epistemological_stance: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    ontology_config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    archetype: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    avatar_config: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<ActorProfile(id={self.id}, name='{self.name}', stance='{self.epistemological_stance}')>"
