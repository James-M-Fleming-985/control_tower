"""Training pipeline client — orchestrates self-hosted avatar training.

Coordinates between the main platform and the Dell GPU service
(LivePortrait feature extraction + SadTalker audio-to-motion).

Training flow:
    1. Generate/upload portrait → save to /static/portraits/
    2. POST portrait to Dell service /api/train (LivePortrait feature extraction)
    3. Dell service extracts appearance features, caches them, reports quality
    4. Update actor's avatar_config with training status + metrics
"""

from __future__ import annotations

import logging

import httpx

from epistemic_platform.config import get_settings

logger = logging.getLogger(__name__)


def _resolve_base_url() -> str:
    """Convert avatar_service_url (WS) to HTTP base URL for REST calls."""
    settings = get_settings()
    url = (settings.avatar_service_url or "").strip()
    if not url:
        raise RuntimeError(
            "AVATAR_SERVICE_URL not configured — set it to the Dell service address"
        )
    # Convert ws:// → http://, strip trailing /ws/avatar path
    url = url.replace("wss://", "https://").replace("ws://", "http://")
    if "/ws/" in url:
        url = url[: url.index("/ws/")]
    return url.rstrip("/")


async def train_actor(actor_name: str, portrait_bytes: bytes) -> dict:
    """Send portrait to Dell service for LivePortrait feature extraction.

    Returns:
        dict with keys: status, face_quality_score, features_path, error
    """
    base = _resolve_base_url()
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{base}/api/train",
            files={"portrait": (f"{actor_name}.png", portrait_bytes, "image/png")},
            data={"actor_name": actor_name},
        )
        resp.raise_for_status()
        return resp.json()


async def get_training_status(actor_name: str) -> dict:
    """Check training status for an actor on the Dell service."""
    base = _resolve_base_url()
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{base}/api/training-status/{actor_name}")
        resp.raise_for_status()
        return resp.json()


async def run_test_inference(actor_name: str, text: str) -> bytes:
    """Run a test inference on Dell service and return MP4 preview bytes."""
    base = _resolve_base_url()
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{base}/api/test",
            json={"actor_name": actor_name, "text": text},
        )
        resp.raise_for_status()
        return resp.content


async def get_service_health() -> dict:
    """Check Dell GPU service health (GPU, models, cached features)."""
    try:
        base = _resolve_base_url()
    except RuntimeError:
        return {"status": "not_configured"}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base}/health")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}
