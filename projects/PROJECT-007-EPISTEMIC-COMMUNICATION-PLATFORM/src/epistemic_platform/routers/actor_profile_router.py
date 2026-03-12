from __future__ import annotations

"""ActorProfile router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.auth.dependencies import get_current_user
from epistemic_platform.database import get_db
from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.repositories.actor_profile_repository import ActorProfileRepository
from epistemic_platform.schemas.actor_profile_schemas import (
    ActorProfileCreate,
    ActorProfileRead,
    ActorProfileUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[ActorProfileRead])
async def list_actors(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ActorProfileRepository(db)
    return await repo.list(skip=skip, limit=limit, active_only=active_only)


@router.get("/stance/{stance}", response_model=list[ActorProfileRead])
async def list_by_stance(
    stance: str,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ActorProfileRepository(db)
    return await repo.get_by_stance(stance)


@router.get("/{actor_id}", response_model=ActorProfileRead)
async def get_actor(
    actor_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ActorProfileRepository(db)
    actor = await repo.get(actor_id)
    if not actor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")
    return actor


@router.post("/", response_model=ActorProfileRead, status_code=status.HTTP_201_CREATED)
async def create_actor(
    data: ActorProfileCreate,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ActorProfileRepository(db)
    return await repo.create(data)


@router.patch("/{actor_id}", response_model=ActorProfileRead)
async def update_actor(
    actor_id: int,
    data: ActorProfileUpdate,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ActorProfileRepository(db)
    actor = await repo.update(actor_id, data)
    if not actor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")
    return actor


@router.delete("/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_actor(
    actor_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    repo = ActorProfileRepository(db)
    deleted = await repo.delete(actor_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")
