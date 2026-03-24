from __future__ import annotations

"""ConversationSession database model."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from epistemic_platform.models.base import BaseModel


class ConversationSession(BaseModel):
    __tablename__ = "conversation_sessions"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    actor_id: Mapped[int] = mapped_column(Integer, ForeignKey("actor_profiles.id"), nullable=False)
    scenario_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("scenario_definitions.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    mode: Mapped[str] = mapped_column(String(10), default="text", nullable=False)
    messages: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    coaching_annotations: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    trilemma_state: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    turn_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("UserProfile", lazy="selectin")
    actor = relationship("ActorProfile", lazy="selectin")
    scenario = relationship("ScenarioDefinition", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ConversationSession(id={self.id}, status='{self.status}', turns={self.turn_count})>"
