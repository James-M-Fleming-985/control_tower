from __future__ import annotations

"""ActorProfile router."""

import logging
from pathlib import Path

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

logger = logging.getLogger(__name__)

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


@router.post("/{actor_id}/generate-portrait", response_model=ActorProfileRead)
async def generate_actor_portrait(
    actor_id: int,
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    """Generate a DALL-E 3 portrait for this actor and store in avatar_config."""
    from epistemic_platform.engine.portrait_generator import generate_portrait

    repo = ActorProfileRepository(db)
    actor = await repo.get(actor_id)
    if not actor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")

    # Save to static/portraits/
    static_dir = Path(__file__).parent.parent / "static" / "portraits"

    try:
        avatar_config = await generate_portrait(
            actor_name=actor.name,
            description=actor.description or "",
            archetype=actor.archetype,
            save_dir=static_dir,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception:
        logger.exception("Portrait generation failed for actor %d", actor_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Portrait generation failed",
        )

    update_data = ActorProfileUpdate(avatar_config=avatar_config)
    updated = await repo.update(actor_id, update_data)
    await db.commit()
    return updated


@router.post("/generate-all-portraits")
async def generate_all_actor_portraits(
    db: AsyncSession = Depends(get_db),
    _user: UserProfile = Depends(get_current_user),
):
    """Generate portraits for all actors that don't have one yet."""
    from epistemic_platform.engine.portrait_generator import generate_portrait

    repo = ActorProfileRepository(db)
    actors = await repo.list(active_only=True)
    static_dir = Path(__file__).parent.parent / "static" / "portraits"

    results = []
    for actor in actors:
        if actor.avatar_config and actor.avatar_config.get("portrait_url"):
            results.append({"actor": actor.name, "status": "skipped", "reason": "already has portrait"})
            continue
        try:
            avatar_config = await generate_portrait(
                actor_name=actor.name,
                description=actor.description or "",
                archetype=actor.archetype,
                save_dir=static_dir,
            )
            update_data = ActorProfileUpdate(avatar_config=avatar_config)
            await repo.update(actor.id, update_data)
            results.append({"actor": actor.name, "status": "generated", "url": avatar_config.get("portrait_url")})
        except Exception as e:
            logger.exception("Portrait generation failed for %s", actor.name)
            results.append({"actor": actor.name, "status": "error", "detail": str(e)})

    await db.commit()
    return {"results": results}
