"""Avatar session router — manages HeyGen streaming avatar sessions.

Provides endpoints to create/start/speak/interrupt/stop avatar sessions.
The frontend connects to HeyGen's LiveKit server directly for video;
these endpoints handle the control plane.

Admin-only training pipeline endpoints let admins generate portraits,
trigger feature extraction on the Dell GPU service, and preview results.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from epistemic_platform.auth.dependencies import get_current_user
from epistemic_platform.auth.admin_guard import require_admin
from epistemic_platform.config import get_settings
from epistemic_platform.database import async_session_factory
from epistemic_platform.engine.heygen_client import HeyGenClient
from epistemic_platform.models.user_profile import UserProfile
from epistemic_platform.repositories.actor_profile_repository import ActorProfileRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/avatar", tags=["avatar"])

# Package root for /static/portraits
_PACKAGE_DIR = Path(__file__).resolve().parent.parent


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


# ─── Admin-only Avatar Lab endpoints ─────────────────────────────────────────


class ManualAssignRequest(BaseModel):
    heygen_avatar_id: str


@router.get("/stock-library")
async def list_stock_library(
    user: UserProfile = Depends(require_admin),
) -> list[dict[str, Any]]:
    """Return full HeyGen stock avatar catalogue with previews (admin only)."""
    settings = get_settings()
    if not settings.heygen_api_key:
        raise HTTPException(status_code=503, detail="HeyGen API key not configured")

    client = HeyGenClient()
    try:
        avatars = await client.list_avatars()
        # Return a simplified view for the frontend grid
        return [
            {
                "avatar_id": a.get("avatar_id", ""),
                "avatar_name": a.get("avatar_name", ""),
                "gender": a.get("gender", ""),
                "preview_image_url": (
                    a.get("preview_image_url")
                    or a.get("preview_url")
                    or ""
                ),
            }
            for a in avatars
        ]
    except Exception as e:
        logger.exception("Failed to list HeyGen avatars")
        raise HTTPException(status_code=502, detail=f"HeyGen avatar listing failed: {e}")
    finally:
        await client.close()


@router.put("/{actor_id}/assign")
async def manual_assign_avatar(
    actor_id: int,
    req: ManualAssignRequest,
    user: UserProfile = Depends(require_admin),
) -> dict[str, Any]:
    """Manually assign a specific HeyGen avatar to an actor (admin only)."""
    settings = get_settings()
    if not settings.heygen_api_key:
        raise HTTPException(status_code=503, detail="HeyGen API key not configured")

    # Verify avatar exists in HeyGen library
    client = HeyGenClient()
    try:
        all_avatars = await client.list_avatars()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"HeyGen API error: {e}")
    finally:
        await client.close()

    target = next((a for a in all_avatars if a.get("avatar_id") == req.heygen_avatar_id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Avatar '{req.heygen_avatar_id}' not found in HeyGen library")

    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")

        new_config = {
            **(actor.avatar_config or {}),
            "heygen_avatar_id": req.heygen_avatar_id,
            "heygen_avatar_name": target.get("avatar_name", ""),
            "heygen_preview_url": (
                target.get("preview_image_url")
                or target.get("preview_url")
                or ""
            ),
            "auto_assigned": False,
        }
        actor.avatar_config = new_config
        await db.commit()

        return {
            "status": "ok",
            "actor_id": actor_id,
            "actor_name": actor.name,
            "heygen_avatar_id": req.heygen_avatar_id,
            "heygen_avatar_name": target.get("avatar_name", ""),
        }


@router.delete("/{actor_id}/assign")
async def remove_avatar_assignment(
    actor_id: int,
    user: UserProfile = Depends(require_admin),
) -> dict[str, str]:
    """Remove HeyGen avatar assignment from an actor (reverts to static)."""
    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")

        cfg = actor.avatar_config or {}
        actor.avatar_config = {
            k: v for k, v in cfg.items()
            if k not in ("heygen_avatar_id", "heygen_avatar_name", "heygen_preview_url", "auto_assigned")
        }
        await db.commit()
        return {"status": "ok", "actor_name": actor.name}


@router.post("/{actor_id}/preview")
async def preview_avatar(
    actor_id: int,
    user: UserProfile = Depends(require_admin),
) -> dict[str, Any]:
    """Start a short preview session for an actor's assigned avatar (admin only).

    Returns LiveKit session details for the frontend to render a 10-sec sample.
    """
    settings = get_settings()
    if not settings.heygen_api_key:
        raise HTTPException(status_code=503, detail="HeyGen API key not configured")

    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")

        avatar_config = actor.avatar_config or {}
        heygen_avatar_id = avatar_config.get("heygen_avatar_id")
        if not heygen_avatar_id:
            raise HTTPException(status_code=400, detail=f"Actor '{actor.name}' has no avatar assigned")

        voice_id = (actor.ontology_config or {}).get("voice_id") or settings.elevenlabs_default_voice_id

    client = HeyGenClient()
    try:
        session_data = await client.create_session(
            avatar_id=heygen_avatar_id,
            voice_id=voice_id,
            quality="medium",
        )
        await client.start_session(session_data["session_id"])

        # Queue a short sample utterance
        sample_text = f"Hello, I am {actor.name}. This is a preview of my avatar."
        await client.speak(session_data["session_id"], sample_text)

        return {
            **session_data,
            "avatar_id": heygen_avatar_id,
            "actor_name": actor.name,
            "sample_text": sample_text,
        }
    except Exception as e:
        logger.exception("Failed to create preview session for actor %d", actor_id)
        raise HTTPException(status_code=502, detail=f"HeyGen preview failed: {e}")
    finally:
        await client.close()


# ─── Training Pipeline (Self-Hosted Avatar) ──────────────────────────────────


class GeneratePortraitRequest(BaseModel):
    model: str = "dalle3"  # "dalle3" | "flux1"


class TrainRequest(BaseModel):
    force: bool = False  # Re-extract even if features already cached


class TestRequest(BaseModel):
    text: str = "Hello, this is a test of my animated avatar."


@router.post("/{actor_id}/generate-portrait")
async def generate_actor_portrait(
    actor_id: int,
    req: GeneratePortraitRequest,
    user: UserProfile = Depends(require_admin),
) -> dict[str, Any]:
    """Generate a new AI portrait for an actor (DALL-E 3 or Flux.1 Dev)."""
    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")

        # Update training status
        cfg = dict(actor.avatar_config or {})
        cfg["training_status"] = "generating_portrait"
        actor.avatar_config = cfg
        await db.commit()

        save_dir = _PACKAGE_DIR / "static" / "portraits"
        try:
            if req.model == "flux1":
                from epistemic_platform.engine.portrait_generator import (
                    generate_portrait_flux1,
                )

                result = await generate_portrait_flux1(
                    actor_name=actor.name,
                    description=actor.description or "",
                    archetype=actor.archetype,
                    save_dir=save_dir,
                )
            else:
                from epistemic_platform.engine.portrait_generator import (
                    generate_portrait,
                )

                result = await generate_portrait(
                    actor_name=actor.name,
                    description=actor.description or "",
                    archetype=actor.archetype,
                    save_dir=save_dir,
                )

            # Update avatar_config with portrait info
            cfg["portrait_url"] = result.get("portrait_url", "")
            cfg["portrait_source"] = result.get("portrait_source", req.model)
            cfg["portrait_generated_at"] = datetime.now(timezone.utc).isoformat()
            cfg["training_status"] = "portrait_ready"
            actor.avatar_config = cfg
            await db.commit()

            return {
                "status": "ok",
                "actor_name": actor.name,
                "portrait_url": cfg["portrait_url"],
                "portrait_source": cfg["portrait_source"],
            }

        except Exception as e:
            cfg["training_status"] = "failed"
            cfg["training_error"] = str(e)
            actor.avatar_config = cfg
            await db.commit()
            logger.exception("Portrait generation failed for actor %d", actor_id)
            raise HTTPException(
                status_code=502,
                detail=f"Portrait generation failed: {e}",
            )


@router.post("/{actor_id}/upload-portrait")
async def upload_actor_portrait(
    actor_id: int,
    portrait: UploadFile = File(...),
    user: UserProfile = Depends(require_admin),
) -> dict[str, Any]:
    """Upload a custom portrait image for an actor."""
    if not portrait.content_type or not portrait.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    content = await portrait.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB max
        raise HTTPException(status_code=400, detail="Image must be under 10 MB")

    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")

        # Save to static/portraits
        save_dir = _PACKAGE_DIR / "static" / "portraits"
        save_dir.mkdir(parents=True, exist_ok=True)
        ext = portrait.filename.rsplit(".", 1)[-1] if portrait.filename and "." in portrait.filename else "png"
        filename = f"{actor.name.lower().replace(' ', '_')}_portrait.{ext}"
        filepath = save_dir / filename
        filepath.write_bytes(content)

        # Update avatar_config
        cfg = dict(actor.avatar_config or {})
        cfg["portrait_url"] = f"/static/portraits/{filename}"
        cfg["portrait_source"] = "uploaded"
        cfg["portrait_generated_at"] = datetime.now(timezone.utc).isoformat()
        cfg["training_status"] = "portrait_ready"
        # Clear any previous training state
        cfg.pop("training_error", None)
        actor.avatar_config = cfg
        await db.commit()

        return {
            "status": "ok",
            "actor_name": actor.name,
            "portrait_url": cfg["portrait_url"],
        }


@router.post("/{actor_id}/train")
async def train_actor_avatar(
    actor_id: int,
    req: TrainRequest,
    user: UserProfile = Depends(require_admin),
) -> dict[str, Any]:
    """Trigger LivePortrait feature extraction on the Dell GPU service.

    Sends the actor's portrait to the Dell service which:
    1. Extracts appearance features via LivePortrait
    2. Caches features for real-time inference
    3. Reports face quality score
    """
    from epistemic_platform.engine.training_pipeline import train_actor

    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")

        cfg = dict(actor.avatar_config or {})
        portrait_url = cfg.get("portrait_url")
        if not portrait_url:
            raise HTTPException(
                status_code=400,
                detail="No portrait available — generate or upload one first",
            )

        # Skip if already trained (unless force)
        if cfg.get("self_hosted_ready") and not req.force:
            return {
                "status": "already_trained",
                "actor_name": actor.name,
                "face_quality_score": cfg.get("face_quality_score"),
            }

        # Load portrait bytes
        portrait_path = _PACKAGE_DIR / portrait_url.lstrip("/")
        if not portrait_path.exists():
            raise HTTPException(status_code=400, detail="Portrait file not found on disk")

        cfg["training_status"] = "extracting_features"
        cfg["training_started_at"] = datetime.now(timezone.utc).isoformat()
        cfg.pop("training_error", None)
        actor.avatar_config = cfg
        await db.commit()

    # Send to Dell service (outside DB session to avoid long-held connections)
    try:
        result = await train_actor(actor.name, portrait_path.read_bytes())
    except Exception as e:
        async with async_session_factory() as db:
            actor_repo = ActorProfileRepository(db)
            actor = await actor_repo.get(actor_id)
            cfg = dict(actor.avatar_config or {})
            cfg["training_status"] = "failed"
            cfg["training_error"] = str(e)
            actor.avatar_config = cfg
            await db.commit()
        logger.exception("Training failed for actor %d", actor_id)
        raise HTTPException(status_code=502, detail=f"Training failed: {e}")

    # Update with results from Dell service
    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(actor_id)
        cfg = dict(actor.avatar_config or {})
        cfg["training_status"] = "ready"
        cfg["training_completed_at"] = datetime.now(timezone.utc).isoformat()
        cfg["face_quality_score"] = result.get("face_quality_score")
        cfg["self_hosted_ready"] = True
        cfg["avatar_source"] = "self_hosted"
        actor.avatar_config = cfg
        await db.commit()

    return {
        "status": "ok",
        "actor_name": actor.name,
        "face_quality_score": result.get("face_quality_score"),
        "training_completed_at": cfg["training_completed_at"],
    }


@router.get("/{actor_id}/training-status")
async def get_training_status(
    actor_id: int,
    user: UserProfile = Depends(require_admin),
) -> dict[str, Any]:
    """Get training pipeline status for an actor."""
    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")

        cfg = actor.avatar_config or {}
        return {
            "actor_id": actor.id,
            "actor_name": actor.name,
            "training_status": cfg.get("training_status", "idle"),
            "portrait_url": cfg.get("portrait_url"),
            "portrait_source": cfg.get("portrait_source"),
            "portrait_generated_at": cfg.get("portrait_generated_at"),
            "training_started_at": cfg.get("training_started_at"),
            "training_completed_at": cfg.get("training_completed_at"),
            "training_error": cfg.get("training_error"),
            "face_quality_score": cfg.get("face_quality_score"),
            "self_hosted_ready": cfg.get("self_hosted_ready", False),
            "avatar_source": cfg.get("avatar_source", "static"),
        }


@router.post("/{actor_id}/test")
async def test_actor_avatar(
    actor_id: int,
    req: TestRequest,
    user: UserProfile = Depends(require_admin),
) -> Any:
    """Run test inference on Dell service — returns MP4 preview video."""
    from fastapi.responses import Response
    from epistemic_platform.engine.training_pipeline import run_test_inference

    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")

        cfg = actor.avatar_config or {}
        if not cfg.get("self_hosted_ready"):
            raise HTTPException(
                status_code=400,
                detail="Actor not trained yet — run training first",
            )

    try:
        video_bytes = await run_test_inference(actor.name, req.text)
        return Response(
            content=video_bytes,
            media_type="video/mp4",
            headers={"Content-Disposition": f"inline; filename={actor.name}_test.mp4"},
        )
    except Exception as e:
        logger.exception("Test inference failed for actor %d", actor_id)
        raise HTTPException(status_code=502, detail=f"Test inference failed: {e}")


@router.get("/{actor_id}/quality-report")
async def get_quality_report(
    actor_id: int,
    user: UserProfile = Depends(require_admin),
) -> dict[str, Any]:
    """Get quality metrics for a trained self-hosted avatar."""
    from epistemic_platform.engine.training_pipeline import get_service_health

    async with async_session_factory() as db:
        actor_repo = ActorProfileRepository(db)
        actor = await actor_repo.get(actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")

        cfg = actor.avatar_config or {}

        # Also get Dell service health
        service_health = await get_service_health()

        return {
            "actor_id": actor.id,
            "actor_name": actor.name,
            "self_hosted_ready": cfg.get("self_hosted_ready", False),
            "portrait_source": cfg.get("portrait_source"),
            "face_quality_score": cfg.get("face_quality_score"),
            "training_completed_at": cfg.get("training_completed_at"),
            "avatar_source": cfg.get("avatar_source", "static"),
            "service_health": service_health,
        }
