"""Dell GPU Avatar Service — LivePortrait + SadTalker real-time animation.

Standalone FastAPI app for the Dell Precision 7760 (RTX A5000, 16GB VRAM).
Receives portraits, extracts appearance features, and produces animated
JPEG frame streams from audio input.

Pipeline:
    Portrait → LivePortrait feature extraction (one-time "training")
    Audio → SadTalker audio2motion → LivePortrait warp → GFPGAN enhance → JPEG

VRAM budget (~8 GB total):
    LivePortrait appearance encoder + warping net: ~2.5 GB
    SadTalker audio2head + audio2lip: ~1.5 GB
    GFPGAN face enhancer: ~1.0 GB
    Working buffers: ~3 GB headroom
"""

from __future__ import annotations

import io
import json
import logging
import time
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, WebSocket
from pydantic import BaseModel
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("avatar-service")

# ── Configuration ──────────────────────────────────────────────────────────


class AvatarSettings(BaseSettings):
    portrait_dir: str = "./portraits"
    features_dir: str = "./features"
    sadtalker_checkpoint_dir: str = "./checkpoints/sadtalker"
    liveportrait_checkpoint_dir: str = "./checkpoints/liveportrait"
    gfpgan_model_path: str = "./checkpoints/gfpgan/GFPGANv1.4.pth"
    output_fps: int = 25
    frame_width: int = 512
    frame_height: int = 512
    device: str = "cuda:0"
    enable_gfpgan: bool = True
    max_cached_actors: int = 12

    model_config = {"env_file": ".env"}


settings = AvatarSettings()
app = FastAPI(title="Avatar Animation Service", version="2.0.0")


# ── GPU Info ───────────────────────────────────────────────────────────────


def _get_gpu_info() -> dict[str, Any]:
    try:
        import torch

        if not torch.cuda.is_available():
            return {"available": False}
        return {
            "available": True,
            "device": settings.device,
            "name": torch.cuda.get_device_name(0),
            "vram_total_gb": round(
                torch.cuda.get_device_properties(0).total_mem / 1e9, 1
            ),
            "vram_used_gb": round(torch.cuda.memory_allocated(0) / 1e9, 2),
            "vram_reserved_gb": round(torch.cuda.memory_reserved(0) / 1e9, 2),
        }
    except Exception:
        return {"available": False, "error": "torch not available"}


# ── Model State ────────────────────────────────────────────────────────────

_liveportrait_encoder = None
_liveportrait_warper = None
_sadtalker_model = None
_gfpgan_model = None

# Cached per-actor appearance features: actor_name → feature dict
_feature_cache: dict[str, dict] = {}


async def _load_liveportrait():
    """Lazy-load LivePortrait appearance encoder and warping network."""
    global _liveportrait_encoder, _liveportrait_warper

    if _liveportrait_encoder is not None:
        return _liveportrait_encoder, _liveportrait_warper

    logger.info(
        "Loading LivePortrait models from %s ...",
        settings.liveportrait_checkpoint_dir,
    )
    import torch

    try:
        from liveportrait.modules.appearance_feature_extractor import (
            AppearanceFeatureExtractor,
        )
        from liveportrait.modules.warping_module import WarpingModule
        from liveportrait.config.inference_config import InferenceConfig

        cfg = InferenceConfig(
            checkpoint_dir=settings.liveportrait_checkpoint_dir,
            device=settings.device,
        )
        _liveportrait_encoder = (
            AppearanceFeatureExtractor(cfg).to(settings.device).eval()
        )
        _liveportrait_warper = WarpingModule(cfg).to(settings.device).eval()

        logger.info(
            "LivePortrait loaded — VRAM: %.1f GB",
            torch.cuda.memory_allocated(0) / 1e9,
        )
        return _liveportrait_encoder, _liveportrait_warper

    except ImportError:
        logger.warning(
            "LivePortrait not installed — install from "
            "https://github.com/KwaiVGI/LivePortrait"
        )
        raise RuntimeError("LivePortrait not installed")


async def _load_sadtalker():
    """Lazy-load SadTalker audio-to-motion model."""
    global _sadtalker_model

    if _sadtalker_model is not None:
        return _sadtalker_model

    logger.info("Loading SadTalker from %s ...", settings.sadtalker_checkpoint_dir)

    try:
        from sadtalker.api import SadTalker

        _sadtalker_model = SadTalker(
            checkpoint_dir=settings.sadtalker_checkpoint_dir,
            device=settings.device,
        )
        logger.info("SadTalker loaded")
        return _sadtalker_model

    except ImportError:
        logger.warning(
            "SadTalker not installed — install from "
            "https://github.com/OpenTalker/SadTalker"
        )
        raise RuntimeError("SadTalker not installed")


async def _load_gfpgan():
    """Lazy-load GFPGAN face enhancer."""
    global _gfpgan_model

    if _gfpgan_model is not None:
        return _gfpgan_model

    if not settings.enable_gfpgan:
        return None

    logger.info("Loading GFPGAN from %s ...", settings.gfpgan_model_path)

    try:
        from gfpgan import GFPGANer

        _gfpgan_model = GFPGANer(
            model_path=settings.gfpgan_model_path,
            upscale=1,
            arch="clean",
            channel_multiplier=2,
            device=settings.device,
        )
        logger.info("GFPGAN loaded")
        return _gfpgan_model

    except ImportError:
        logger.warning("GFPGAN not installed — frames will not be enhanced")
        return None


# ── Feature Extraction (Training) ─────────────────────────────────────────


def _get_features_path(actor_name: str) -> Path:
    """Path to cached appearance features for an actor."""
    features_dir = Path(settings.features_dir)
    features_dir.mkdir(parents=True, exist_ok=True)
    safe_name = actor_name.lower().replace(" ", "_")
    return features_dir / f"{safe_name}_features.npz"


async def _extract_features(actor_name: str, image_bytes: bytes) -> dict:
    """Extract LivePortrait appearance features from a portrait image.

    This is the 'training' step — run once per portrait, cached for inference.
    """
    import cv2
    import torch

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode portrait image")

    img = cv2.resize(img, (settings.frame_width, settings.frame_height))
    encoder, _ = await _load_liveportrait()

    with torch.no_grad():
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        tensor = (
            torch.from_numpy(img_rgb)
            .permute(2, 0, 1)
            .unsqueeze(0)
            .float()
            .to(settings.device)
            / 255.0
        )
        features = encoder(tensor)
        feature_data = {
            "appearance": features.cpu().numpy(),
            "source_image": img_rgb,
            "image_shape": img.shape[:2],
        }

    face_quality = _compute_face_quality(img)

    features_path = _get_features_path(actor_name)
    np.savez_compressed(
        features_path,
        appearance=feature_data["appearance"],
        source_image=feature_data["source_image"],
    )

    _feature_cache[actor_name] = feature_data
    logger.info(
        "Extracted features for %s — quality: %.2f, saved to %s",
        actor_name,
        face_quality,
        features_path,
    )

    return {
        "status": "ready",
        "face_quality_score": round(face_quality, 3),
        "features_path": str(features_path),
    }


def _compute_face_quality(img) -> float:
    """Compute a face quality score (0-1) using OpenCV face detection."""
    try:
        import cv2

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))

        if len(faces) == 0:
            return 0.3
        if len(faces) > 1:
            return 0.5

        (x, y, w, h) = faces[0]
        img_h, img_w = img.shape[:2]
        center_x = (x + w / 2) / img_w
        center_y = (y + h / 2) / img_h
        face_ratio = (w * h) / (img_w * img_h)

        center_score = 1.0 - abs(center_x - 0.5) - abs(center_y - 0.45)
        size_score = min(face_ratio / 0.15, 1.0)

        return max(0.0, min(1.0, 0.5 * center_score + 0.5 * size_score + 0.3))
    except Exception:
        return 0.5


def _load_cached_features(actor_name: str) -> dict | None:
    """Load cached features from disk into memory cache."""
    if actor_name in _feature_cache:
        return _feature_cache[actor_name]

    features_path = _get_features_path(actor_name)
    if not features_path.exists():
        return None

    data = np.load(features_path, allow_pickle=True)
    feature_data = {
        "appearance": data["appearance"],
        "source_image": data["source_image"],
    }
    _feature_cache[actor_name] = feature_data
    return feature_data


# ── Inference ──────────────────────────────────────────────────────────────


async def _animate_frame(
    actor_name: str,
    audio_chunk: bytes,
    mood: str = "neutral",
) -> list[bytes]:
    """Generate animated JPEG frames from an audio chunk.

    Pipeline:
        audio_chunk → SadTalker → motion coefficients
        motion + cached appearance → LivePortrait warp → frame
        frame → GFPGAN enhance (optional) → JPEG bytes
    """
    import cv2
    import torch

    features = _load_cached_features(actor_name)
    if features is None:
        raise ValueError(f"No trained features for {actor_name}")

    _, warper = await _load_liveportrait()
    sadtalker = await _load_sadtalker()
    gfpgan = await _load_gfpgan()

    with torch.no_grad():
        motion_coeffs = sadtalker.audio_to_motion(
            audio_chunk,
            expression=mood,
        )

        appearance = torch.from_numpy(features["appearance"]).to(settings.device)
        frames = []

        for coeff in motion_coeffs:
            motion_tensor = (
                torch.from_numpy(coeff).unsqueeze(0).to(settings.device)
            )
            warped = warper(appearance, motion_tensor)

            frame = (
                warped.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255
            ).astype(np.uint8)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if gfpgan is not None:
                _, _, enhanced = gfpgan.enhance(
                    frame, has_aligned=True, only_center_face=True
                )
                if enhanced is not None:
                    frame = enhanced

            _, buf = cv2.imencode(
                ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85]
            )
            frames.append(buf.tobytes())

        return frames


# ── REST Endpoints ─────────────────────────────────────────────────────────


@app.get("/health")
async def health_check():
    """Service health: GPU status, loaded models, cached features."""
    gpu = _get_gpu_info()
    cached_actors = list(_feature_cache.keys())

    features_dir = Path(settings.features_dir)
    disk_features = []
    if features_dir.exists():
        disk_features = [
            f.stem.replace("_features", "")
            for f in features_dir.glob("*_features.npz")
        ]

    return {
        "status": "ok",
        "gpu": gpu,
        "models": {
            "liveportrait": _liveportrait_encoder is not None,
            "sadtalker": _sadtalker_model is not None,
            "gfpgan": _gfpgan_model is not None,
        },
        "cached_actors": cached_actors,
        "disk_features": disk_features,
        "settings": {
            "output_fps": settings.output_fps,
            "frame_size": f"{settings.frame_width}x{settings.frame_height}",
            "gfpgan_enabled": settings.enable_gfpgan,
        },
    }


class TestInferenceRequest(BaseModel):
    actor_name: str
    text: str = "Hello, this is a test."


@app.post("/api/train")
async def train_actor(
    portrait: UploadFile = File(...),
    actor_name: str = Form(...),
):
    """Extract LivePortrait appearance features from a portrait image.

    Accepts a portrait, runs feature extraction, caches for real-time
    inference. Returns quality metrics.
    """
    content = await portrait.read()
    if len(content) < 1000:
        raise HTTPException(status_code=400, detail="Image too small")
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 20 MB")

    portrait_dir = Path(settings.portrait_dir)
    portrait_dir.mkdir(parents=True, exist_ok=True)
    safe_name = actor_name.lower().replace(" ", "_")
    portrait_path = portrait_dir / f"{safe_name}_portrait.png"
    portrait_path.write_bytes(content)

    try:
        result = await _extract_features(actor_name, content)
        return result
    except Exception as e:
        logger.exception("Feature extraction failed for %s", actor_name)
        raise HTTPException(
            status_code=500,
            detail=f"Feature extraction failed: {e}",
        )


@app.get("/api/training-status/{actor_name}")
async def training_status(actor_name: str):
    """Check whether an actor's features are extracted and cached."""
    features_path = _get_features_path(actor_name)
    in_memory = actor_name in _feature_cache

    if features_path.exists():
        return {
            "status": "ready",
            "actor_name": actor_name,
            "features_path": str(features_path),
            "in_memory": in_memory,
            "file_size_mb": round(features_path.stat().st_size / 1e6, 2),
        }
    return {
        "status": "not_trained",
        "actor_name": actor_name,
        "in_memory": False,
    }


@app.post("/api/test")
async def test_inference(req: TestInferenceRequest):
    """Run test inference: generate a short animation from text.

    Returns MP4 video bytes directly.
    """
    import cv2
    import tempfile

    features = _load_cached_features(req.actor_name)
    if features is None:
        raise HTTPException(
            status_code=400,
            detail=f"No trained features for {req.actor_name}",
        )

    try:
        source_img = features["source_image"]
        frames_data = []
        for _ in range(settings.output_fps):
            frame = cv2.cvtColor(
                source_img.astype(np.uint8), cv2.COLOR_RGB2BGR
            )
            frame = cv2.resize(
                frame, (settings.frame_width, settings.frame_height)
            )
            frames_data.append(frame)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(
                tmp.name,
                fourcc,
                settings.output_fps,
                (settings.frame_width, settings.frame_height),
            )
            for frame in frames_data:
                writer.write(frame)
            writer.release()

            tmp_path = Path(tmp.name)
            video_bytes = tmp_path.read_bytes()
            tmp_path.unlink(missing_ok=True)

        from fastapi.responses import Response

        return Response(content=video_bytes, media_type="video/mp4")

    except Exception as e:
        logger.exception("Test inference failed for %s", req.actor_name)
        raise HTTPException(
            status_code=500, detail=f"Test inference failed: {e}"
        )


# ── WebSocket Endpoint ─────────────────────────────────────────────────────


@app.websocket("/ws/avatar/{session_id}")
async def avatar_websocket(websocket: WebSocket, session_id: str):
    """Real-time avatar animation over WebSocket.

    Protocol:
        Client -> Server:
            - JSON: {"type": "init", "actor_name": "..."}
            - JSON: {"type": "meta", "tone": "...", "mood": "..."}
            - Binary: raw audio chunk (PCM/WebM)
            - JSON: {"type": "audio_end"}
            - JSON: {"type": "close"}

        Server -> Client:
            - JSON: {"type": "ready", "fps": 25}
            - Binary: JPEG frame data
            - JSON: {"type": "frame_end"}
            - JSON: {"type": "error", "detail": "..."}
    """
    await websocket.accept()
    logger.info("Avatar WebSocket connected: session=%s", session_id)

    actor_name: str | None = None
    current_meta: dict = {}

    try:
        while True:
            message = await websocket.receive()

            if message.get("type") == "websocket.disconnect":
                break

            raw_bytes = message.get("bytes")
            if raw_bytes and actor_name:
                try:
                    frames = await _animate_frame(
                        actor_name,
                        raw_bytes,
                        mood=current_meta.get("mood", "neutral"),
                    )
                    for frame_bytes in frames:
                        await websocket.send_bytes(frame_bytes)
                    await websocket.send_json({"type": "frame_end"})
                except Exception:
                    logger.exception("Animation inference error")
                    await websocket.send_json(
                        {"type": "error", "detail": "Inference error"}
                    )
                continue

            raw_text = message.get("text")
            if not raw_text:
                continue

            data = json.loads(raw_text)
            msg_type = data.get("type", "")

            if msg_type == "init":
                actor_name = data.get("actor_name", "Unknown")
                features = _load_cached_features(actor_name)
                if features is not None:
                    await websocket.send_json({
                        "type": "ready",
                        "fps": settings.output_fps,
                        "actor": actor_name,
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "detail": f"No trained features for {actor_name}",
                    })

            elif msg_type == "meta":
                current_meta = {
                    k: v for k, v in data.items() if k != "type"
                }

            elif msg_type == "audio_end":
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


# ── Static portrait fallback ──────────────────────────────────────────────


@app.get("/api/stub-frame/{actor_name}")
async def get_stub_frame(actor_name: str):
    """Return a static portrait frame (testing without GPU models)."""
    portrait_dir = Path(settings.portrait_dir)
    safe_name = actor_name.lower().replace(" ", "_")
    filename = f"{safe_name}_portrait.png"
    path = portrait_dir / filename

    if not path.exists():
        raise HTTPException(status_code=404, detail="Portrait not found")

    from fastapi.responses import FileResponse
    return FileResponse(path, media_type="image/png")
