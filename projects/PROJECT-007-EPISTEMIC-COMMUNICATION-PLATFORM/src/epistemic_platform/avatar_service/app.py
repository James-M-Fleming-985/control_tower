"""Avatar Animation Service — MuseTalk lip-sync + LivePortrait expressions.

Standalone FastAPI app designed to run on a GPU workstation (Dell Precision 7760,
RTX A5000 16GB VRAM). Receives audio chunks and returns animated video frames
of the actor's portrait with lip-sync and expression control.

Start with: uvicorn avatar_service.app:app --host 0.0.0.0 --port 8765
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class AvatarSettings(BaseSettings):
    """Configuration for the avatar service."""

    musetalk_path: str = "./MuseTalk"
    portrait_dir: str = "./portraits"
    output_fps: int = 25
    frame_width: int = 512
    frame_height: int = 512
    device: str = "cuda:0"
    # Cloudflare tunnel URL set at runtime
    tunnel_url: str = ""
    # Auth token shared with Railway app
    service_token: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = AvatarSettings()

app = FastAPI(title="Avatar Animation Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── GPU / Model state ─────────────────────────────────────────────────────

_musetalk_pipeline = None
_portrait_cache: dict[str, Any] = {}


def _get_gpu_info() -> dict:
    """Get GPU memory usage info."""
    try:
        import torch

        if torch.cuda.is_available():
            mem = torch.cuda.mem_get_info(0)
            return {
                "gpu_available": True,
                "device_name": torch.cuda.get_device_name(0),
                "vram_free_gb": round(mem[0] / 1e9, 2),
                "vram_total_gb": round(mem[1] / 1e9, 2),
                "vram_used_gb": round((mem[1] - mem[0]) / 1e9, 2),
            }
    except Exception:
        pass
    return {"gpu_available": False}


async def _load_musetalk():
    """Lazy-load MuseTalk pipeline on first request."""
    global _musetalk_pipeline
    if _musetalk_pipeline is not None:
        return _musetalk_pipeline

    logger.info("Loading MuseTalk pipeline from %s ...", settings.musetalk_path)
    try:
        import sys

        sys.path.insert(0, settings.musetalk_path)

        # MuseTalk's inference pipeline
        # This is a placeholder — actual imports depend on MuseTalk version
        from musetalk.utils.preprocessing import get_landmark_and_bbox
        from musetalk.utils.blending import get_image_prepare_material
        from musetalk.models.musetalk import MuseTalk

        pipeline = MuseTalk(device=settings.device)
        pipeline.load_model()
        _musetalk_pipeline = pipeline
        logger.info("MuseTalk pipeline loaded successfully")
        return pipeline
    except ImportError:
        logger.warning(
            "MuseTalk not installed at %s — running in stub mode",
            settings.musetalk_path,
        )
        return None
    except Exception:
        logger.exception("Failed to load MuseTalk pipeline")
        return None


async def _prepare_portrait(actor_name: str, portrait_path: str) -> dict | None:
    """Pre-process a portrait image for MuseTalk (extract landmarks, crop face)."""
    if actor_name in _portrait_cache:
        return _portrait_cache[actor_name]

    path = Path(portrait_path)
    if not path.exists():
        # Try portrait_dir
        path = Path(settings.portrait_dir) / f"{actor_name.lower().replace(' ', '_')}_portrait.png"

    if not path.exists():
        logger.warning("Portrait not found for %s at %s", actor_name, path)
        return None

    pipeline = await _load_musetalk()
    if pipeline is None:
        return None

    try:
        # Pre-process: extract face landmarks, bounding box, reference features
        import cv2
        import numpy as np

        img = cv2.imread(str(path))
        if img is None:
            return None

        # Resize to target dimensions
        img = cv2.resize(img, (settings.frame_width, settings.frame_height))

        # Extract face preparation material (MuseTalk-specific)
        prep = get_image_prepare_material(img)
        _portrait_cache[actor_name] = {
            "image": img,
            "prep": prep,
            "path": str(path),
        }
        logger.info("Prepared portrait for %s", actor_name)
        return _portrait_cache[actor_name]
    except Exception:
        logger.exception("Failed to prepare portrait for %s", actor_name)
        return None


# ── HTTP Endpoints ─────────────────────────────────────────────────────────


@app.get("/health")
async def health_check():
    """Health check with GPU info."""
    gpu_info = _get_gpu_info()
    return {
        "status": "ok",
        "service": "avatar-animation",
        "gpu": gpu_info,
        "musetalk_loaded": _musetalk_pipeline is not None,
        "cached_portraits": list(_portrait_cache.keys()),
    }


class AnimateRequest(BaseModel):
    actor_name: str
    expression: str = "neutral"
    # META tag data for expression control
    meta: dict[str, str] = {}


@app.post("/api/animate")
async def animate_frame(
    audio: UploadFile = File(...),
    actor_name: str = Form(...),
    expression: str = Form("neutral"),
):
    """Generate animated frames from a single audio chunk.

    Returns JPEG frames as multipart response.
    """
    pipeline = await _load_musetalk()
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="MuseTalk pipeline not available — check GPU and installation",
        )

    portrait_data = await _prepare_portrait(actor_name, "")
    if portrait_data is None:
        raise HTTPException(status_code=404, detail=f"Portrait not found for {actor_name}")

    audio_bytes = await audio.read()
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio chunk too small")

    try:
        import cv2
        import numpy as np

        # Run MuseTalk inference: audio → lip coefficients → rendered frame
        frames = pipeline.inference(
            source_image=portrait_data["image"],
            audio_data=audio_bytes,
            prep_material=portrait_data["prep"],
        )

        # Encode frames as JPEG
        result_frames = []
        for frame in frames:
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            result_frames.append(buf.tobytes())

        return {
            "frames": len(result_frames),
            "fps": settings.output_fps,
            # In production, return as streaming multipart or WebSocket
        }
    except Exception:
        logger.exception("Animation inference failed")
        raise HTTPException(status_code=500, detail="Animation inference failed")


# ── WebSocket Endpoint ─────────────────────────────────────────────────────


@app.websocket("/ws/avatar/{session_id}")
async def avatar_websocket(websocket: WebSocket, session_id: str):
    """Real-time avatar animation over WebSocket.

    Protocol:
        Client → Server:
            - JSON: {"type": "init", "actor_name": "...", "portrait_url": "..."}
            - JSON: {"type": "meta", "tone": "...", "mood": "...", ...}
            - Binary: raw audio chunk (PCM/WebM)
            - JSON: {"type": "audio_end"} — flush remaining frames
            - JSON: {"type": "close"}

        Server → Client:
            - JSON: {"type": "ready", "fps": 25}
            - Binary: JPEG frame data
            - JSON: {"type": "frame_end"} — marks end of frame batch for this audio chunk
            - JSON: {"type": "error", "detail": "..."}
    """
    # Optional: verify service token
    # token = websocket.query_params.get("token")
    # if settings.service_token and token != settings.service_token:
    #     await websocket.close(code=1008, reason="Invalid token")
    #     return

    await websocket.accept()
    logger.info("Avatar WebSocket connected: session=%s", session_id)

    actor_name: str | None = None
    portrait_data: dict | None = None
    current_meta: dict = {}

    try:
        while True:
            message = await websocket.receive()

            if message.get("type") == "websocket.disconnect":
                break

            # Binary: audio data for lip-sync
            raw_bytes = message.get("bytes")
            if raw_bytes and portrait_data:
                pipeline = await _load_musetalk()
                if pipeline is None:
                    await websocket.send_json({"type": "error", "detail": "Pipeline not loaded"})
                    continue

                try:
                    import cv2

                    # Run inference
                    frames = pipeline.inference(
                        source_image=portrait_data["image"],
                        audio_data=raw_bytes,
                        prep_material=portrait_data["prep"],
                        expression=current_meta.get("mood", "neutral"),
                    )

                    # Stream JPEG frames
                    for frame in frames:
                        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        await websocket.send_bytes(buf.tobytes())

                    await websocket.send_json({"type": "frame_end"})
                except Exception:
                    logger.exception("Avatar inference error")
                    await websocket.send_json({"type": "error", "detail": "Inference error"})
                continue

            # Text: JSON control messages
            raw_text = message.get("text")
            if not raw_text:
                continue

            data = json.loads(raw_text)
            msg_type = data.get("type", "")

            if msg_type == "init":
                actor_name = data.get("actor_name", "Unknown")
                portrait_url = data.get("portrait_url", "")
                portrait_data = await _prepare_portrait(actor_name, portrait_url)

                if portrait_data:
                    await websocket.send_json({
                        "type": "ready",
                        "fps": settings.output_fps,
                        "actor": actor_name,
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "detail": f"Could not load portrait for {actor_name}",
                    })

            elif msg_type == "meta":
                # Update expression state from META tags
                current_meta = {
                    k: v for k, v in data.items() if k != "type"
                }

            elif msg_type == "audio_end":
                # Flush — no more audio for this turn
                await websocket.send_json({"type": "frame_end"})

            elif msg_type == "close":
                break

    except Exception:
        logger.exception("Avatar WebSocket error for session %s", session_id)
    finally:
        logger.info("Avatar WebSocket closed: session=%s", session_id)
        try:
            await websocket.close()
        except Exception:
            pass


# ── Stub mode for testing without GPU ──────────────────────────────────────

@app.get("/api/stub-frame/{actor_name}")
async def get_stub_frame(actor_name: str):
    """Return a static portrait frame (for testing without MuseTalk)."""
    portrait_dir = Path(settings.portrait_dir)
    filename = f"{actor_name.lower().replace(' ', '_')}_portrait.png"
    path = portrait_dir / filename

    if not path.exists():
        raise HTTPException(status_code=404, detail="Portrait not found")

    from fastapi.responses import FileResponse

    return FileResponse(path, media_type="image/png")
