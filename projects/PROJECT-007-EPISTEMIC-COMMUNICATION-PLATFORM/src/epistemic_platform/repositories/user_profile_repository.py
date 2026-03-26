from __future__ import annotations

"""UserProfile repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.schemas.user_profile_schemas import UserProfileCreate, UserProfileUpdate


class UserProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: int) -> UserProfile | None:
        result = await self.db.execute(select(UserProfile).where(UserProfile.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> UserProfile | None:
        result = await self.db.execute(select(UserProfile).where(UserProfile.email == email))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[UserProfile]:
        result = await self.db.execute(select(UserProfile).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, data: UserProfileCreate, hashed_password: str) -> UserProfile:
        user = UserProfile(
            email=data.email,
            display_name=data.display_name,
            skill_level=data.skill_level,
            preferences=data.preferences,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)  # reload server-generated values (id, timestamps)
        return user

    async def update(self, user_id: int, data: UserProfileUpdate) -> UserProfile | None:
        user = await self.get(user_id)
        if not user:
            return None
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(user, field, value)
        # SQLAlchemy doesn't detect in-place mutations on JSON columns;
        # explicitly flag them so flush() writes the change.
        if "preferences" in updates:
            flag_modified(user, "preferences")
        await self.db.flush()
        await self.db.refresh(user)  # reload server-generated values (updated_at)
        return user

    async def delete(self, user_id: int) -> bool:
        user = await self.get(user_id)
        if not user:
            return False
        self.db.delete(user)
        await self.db.flush()
        return True
