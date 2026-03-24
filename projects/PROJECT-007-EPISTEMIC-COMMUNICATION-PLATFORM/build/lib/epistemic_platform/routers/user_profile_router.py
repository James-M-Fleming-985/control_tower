from __future__ import annotations

"""UserProfile router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.auth.dependencies import get_current_user
from epistemic_platform.database import get_db
from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.repositories.user_profile_repository import UserProfileRepository
from epistemic_platform.schemas.user_profile_schemas import UserProfileRead, UserProfileUpdate

router = APIRouter()


@router.get("/me", response_model=UserProfileRead)
async def get_current_user_profile(
    user: UserProfile = Depends(get_current_user),
):
    return user


@router.patch("/me", response_model=UserProfileRead)
async def update_current_user(
    data: UserProfileUpdate,
    user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserProfileRepository(db)
    updated = await repo.update(user.id, data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated


@router.get("/{user_id}", response_model=UserProfileRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = UserProfileRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
