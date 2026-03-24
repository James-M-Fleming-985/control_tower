from __future__ import annotations

"""ActorProfile repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.models.actor_profile import ActorProfile
from epistemic_platform.schemas.actor_profile_schemas import ActorProfileCreate, ActorProfileUpdate


class ActorProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, actor_id: int) -> ActorProfile | None:
        result = await self.db.execute(select(ActorProfile).where(ActorProfile.id == actor_id))
        return result.scalar_one_or_none()

    async def list(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> list[ActorProfile]:
        query = select(ActorProfile)
        if active_only:
            query = query.where(ActorProfile.is_active.is_(True))
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_stance(self, stance: str) -> list[ActorProfile]:
        result = await self.db.execute(
            select(ActorProfile).where(
                ActorProfile.epistemological_stance == stance,
                ActorProfile.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def create(self, data: ActorProfileCreate) -> ActorProfile:
        actor = ActorProfile(**data.model_dump())
        self.db.add(actor)
        await self.db.flush()
        return actor

    async def update(self, actor_id: int, data: ActorProfileUpdate) -> ActorProfile | None:
        actor = await self.get(actor_id)
        if not actor:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(actor, field, value)
        await self.db.flush()
        return actor

    async def delete(self, actor_id: int) -> bool:
        actor = await self.get(actor_id)
        if not actor:
            return False
        await self.db.delete(actor)
        await self.db.flush()
        return True
