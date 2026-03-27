from __future__ import annotations

"""ConversationSession repository."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.models.conversation_session import ConversationSession
from epistemic_platform.schemas.conversation_session_schemas import (
    ConversationSessionCreate,
    ConversationSessionUpdate,
)


class ConversationSessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, session_id: int) -> ConversationSession | None:
        result = await self.db.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[ConversationSession]:
        result = await self.db.execute(
            select(ConversationSession)
            .where(ConversationSession.user_id == user_id)
            .order_by(ConversationSession.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_active(self, user_id: int) -> list[ConversationSession]:
        result = await self.db.execute(
            select(ConversationSession).where(
                ConversationSession.user_id == user_id,
                ConversationSession.status == "active",
            )
        )
        return list(result.scalars().all())

    async def create(
        self, user_id: int, data: ConversationSessionCreate
    ) -> ConversationSession:
        session = ConversationSession(
            user_id=user_id,
            actor_id=data.actor_id,
            scenario_id=data.scenario_id,
            mode=data.mode,
            status="active",
            messages=[],
            coaching_annotations=[],
            trilemma_state={"current_horn": None, "state": "exploring"},
            turn_count=0,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def update(
        self, session_id: int, data: ConversationSessionUpdate
    ) -> ConversationSession | None:
        session = await self.get(session_id)
        if not session:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(session, field, value)
        await self.db.flush()
        return session

    async def append_message(
        self, session_id: int, message: dict
    ) -> ConversationSession | None:
        session = await self.get(session_id)
        if not session:
            return None
        session.messages = [*session.messages, message]
        session.turn_count = len(
            [m for m in session.messages if m.get("role") == "user"]
        )
        await self.db.flush()
        return session

    async def append_coaching(
        self, session_id: int, annotation: dict
    ) -> ConversationSession | None:
        session = await self.get(session_id)
        if not session:
            return None
        session.coaching_annotations = [*session.coaching_annotations, annotation]
        await self.db.flush()
        return session

    async def update_trilemma_state(
        self, session_id: int, state: dict
    ) -> ConversationSession | None:
        session = await self.get(session_id)
        if not session:
            return None
        session.trilemma_state = state
        await self.db.flush()
        return session

    async def end_session(self, session_id: int) -> ConversationSession | None:
        session = await self.get(session_id)
        if not session:
            return None
        session.status = "completed"
        session.ended_at = datetime.now(timezone.utc)
        await self.db.flush()
        return session

    async def get_debrief_for_parent(
        self, parent_session_id: int
    ) -> ConversationSession | None:
        """Return the most recent debrief session for a given parent session."""
        result = await self.db.execute(
            select(ConversationSession)
            .where(ConversationSession.parent_session_id == parent_session_id)
            .order_by(ConversationSession.started_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_completed_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[ConversationSession]:
        """Return completed sessions for a user, oldest first (for growth tracking).

        Excludes debrief sessions (parent_session_id IS NOT NULL) because they
        lack coaching annotations, trilemma state, and stance data, producing
        near-zero scores that pollute growth charts.
        """
        result = await self.db.execute(
            select(ConversationSession)
            .where(
                ConversationSession.user_id == user_id,
                ConversationSession.status == "completed",
                ConversationSession.parent_session_id.is_(None),
            )
            .order_by(ConversationSession.started_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_recent_completed_by_user(
        self, user_id: int, *, exclude_session_id: int | None = None, limit: int = 10
    ) -> list[ConversationSession]:
        """Return recent completed sessions, newest first.

        Used to build cross-session context for actor prompts.
        Actor relationship is eager-loaded via selectin on the model.
        """
        q = (
            select(ConversationSession)
            .where(
                ConversationSession.user_id == user_id,
                ConversationSession.status == "completed",
                ConversationSession.parent_session_id.is_(None),
            )
            .order_by(ConversationSession.started_at.desc())
            .limit(limit)
        )
        if exclude_session_id is not None:
            q = q.where(ConversationSession.id != exclude_session_id)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def delete(self, session_id: int) -> bool:
        session = await self.get(session_id)
        if not session:
            return False
        self.db.delete(session)
        await self.db.flush()
        return True
