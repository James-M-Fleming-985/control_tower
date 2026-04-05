"""Avatar session router — manages HeyGen streaming avatar sessions.

Provides endpoints to create/start/speak/interrupt/stop avatar sessions.
The frontend connects to HeyGen's LiveKit server directly for video;
these endpoints handle the control plane.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from epistemic_platform.auth.dependencies import get_current_user
from epistemic_platform.config import get_settings
from epistemic_platform.database import async_session_factory
from epistemic_platform.engine.heygen_client import HeyGenClient
from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.repositories.actor_profile_repository import ActorProfileRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/avatar", tags=["avatar"])


class CreateSessionRequest(BaseModel):
    actor_id: int
    quality: str = "medium"


class CreateSessionResponse(BaseModel):
    session_id: str
    access_token: str
    url: str
    avatar_id: str


class SpeakRequest(BaseModel):
    session_id: str
    text: str
    mood: str | None = None


class InterruptRequest(BaseModel):
    session_id: str


class StopRequest(BaseModel):
    session_id: str


@router.post("/session", response_model=CreateSessionResponse)
async def create_avatar_session(
    req: CreateSessionRequest,
    user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Create a HeyGen streaming avatar session for an actor.

    Returns LiveKit connection details for the frontend.
    """
    settings = get_settings()
    if not settings.heygen_api_key:
        raise HTTPException(status_code=503, detail="HeyGen API key not configured")

    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(req.actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")

        # Get HeyGen avatar_id from actor's avatar_config
        avatar_config = actor.avatar_config or {}
        heygen_avatar_id = avatar_config.get("heygen_avatar_id")
        if not heygen_avatar_id:
            raise HTTPException(
                status_code=400,
                detail=f"Actor '{actor.name}' has no HeyGen avatar configured",
            )

        # Get actor's ElevenLabs voice_id
        voice_id = (actor.ontology_config or {}).get("voice_id") or settings.elevenlabs_default_voice_id

    client = HeyGenClient()
    try:
        session_data = await client.create_session(
            avatar_id=heygen_avatar_id,
            voice_id=voice_id,
            quality=req.quality,
        )
        await client.start_session(session_data["session_id"])

        return {
            **session_data,
            "avatar_id": heygen_avatar_id,
        }
    except Exception as e:
        logger.exception("Failed to create HeyGen session for actor %d", req.actor_id)
        raise HTTPException(status_code=502, detail=f"HeyGen session creation failed: {e}")
    finally:
        await client.close()


@router.post("/speak")
async def avatar_speak(
    req: SpeakRequest,
    user: UserProfile = Depends(get_current_user),
) -> dict[str, str]:
    """Send text for the avatar to speak (TaskType.REPEAT — verbatim, no HeyGen LLM)."""
    settings = get_settings()
    if not settings.heygen_api_key:
        raise HTTPException(status_code=503, detail="HeyGen API key not configured")

    emotion = HeyGenClient.mood_to_emotion(req.mood)

    client = HeyGenClient()
    try:
        await client.speak(req.session_id, req.text, emotion=emotion)
        return {"status": "ok"}
    except Exception as e:
        logger.exception("HeyGen speak failed: session=%s", req.session_id)
        raise HTTPException(status_code=502, detail=f"HeyGen speak failed: {e}")
    finally:
        await client.close()


@router.post("/interrupt")
async def avatar_interrupt(
    req: InterruptRequest,
    user: UserProfile = Depends(get_current_user),
) -> dict[str, str]:
    """Interrupt current avatar speech (barge-in)."""
    settings = get_settings()
    if not settings.heygen_api_key:
        raise HTTPException(status_code=503, detail="HeyGen API key not configured")

    client = HeyGenClient()
    try:
        await client.interrupt(req.session_id)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"HeyGen interrupt failed: {e}")
    finally:
        await client.close()


@router.delete("/session/{session_id}")
async def stop_avatar_session(
    session_id: str,
    user: UserProfile = Depends(get_current_user),
) -> dict[str, str]:
    """Stop and destroy a HeyGen streaming session."""
    settings = get_settings()
    if not settings.heygen_api_key:
        raise HTTPException(status_code=503, detail="HeyGen API key not configured")

    client = HeyGenClient()
    try:
        await client.stop_session(session_id)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"HeyGen stop failed: {e}")
    finally:
        await client.close()


@router.post("/assign")
async def reassign_avatars(
    user: UserProfile = Depends(get_current_user),
) -> dict[str, Any]:
    """Re-run automatic HeyGen avatar assignment for all actors.

    Clears existing auto-assigned avatars and re-matches.
    Manually assigned avatars (auto_assigned=false) are preserved.
    """
    settings = get_settings()
    if not settings.heygen_api_key:
        raise HTTPException(status_code=503, detail="HeyGen API key not configured")

    from sqlalchemy import select
    from epistemic_platform.models.actor_profile import ActorProfile
    from epistemic_platform.engine.avatar_assigner import assign_heygen_avatars

    async with async_session_factory() as db:
        # Clear only auto-assigned avatars so they get re-matched
        result = await db.execute(
            select(ActorProfile).where(ActorProfile.is_active.is_(True))
        )
        for actor in result.scalars().all():
            cfg = actor.avatar_config or {}
            if cfg.get("auto_assigned"):
                actor.avatar_config = {
                    k: v for k, v in cfg.items()
                    if k not in ("heygen_avatar_id", "heygen_avatar_name", "heygen_preview_url", "auto_assigned")
                }
        await db.commit()

        count = await assign_heygen_avatars(db)
        return {"status": "ok", "actors_updated": count}


@router.get("/assignments")
async def list_avatar_assignments(
    user: UserProfile = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """List current HeyGen avatar assignments for all actors."""
    from sqlalchemy import select
    from epistemic_platform.models.actor_profile import ActorProfile

    async with async_session_factory() as db:
        result = await db.execute(
            select(ActorProfile).where(ActorProfile.is_active.is_(True))
        )
        assignments = []
        for actor in result.scalars().all():
            cfg = actor.avatar_config or {}
            assignments.append({
                "actor_id": actor.id,
                "actor_name": actor.name,
                "heygen_avatar_id": cfg.get("heygen_avatar_id"),
                "heygen_avatar_name": cfg.get("heygen_avatar_name"),
                "heygen_preview_url": cfg.get("heygen_preview_url"),
                "auto_assigned": cfg.get("auto_assigned", False),
            })
        return assignments
