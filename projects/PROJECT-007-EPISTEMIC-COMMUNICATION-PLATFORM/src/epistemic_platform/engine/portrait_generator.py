"""Portrait generation — DALL-E 3 or Flux.1 Dev (via Replicate) actor headshots.

Generates a professional, consistent portrait for an actor based on their
description and archetype, then stores the URL in avatar_config.
"""

from __future__ import annotations

import asyncio
import base64
import logging
from pathlib import Path

import httpx

from epistemic_platform.config import get_settings

logger = logging.getLogger(__name__)

# Each actor gets a deterministic appearance prompt so regenerations stay consistent.
ACTOR_APPEARANCE: dict[str, str] = {
    "Professor Axelrod": (
        "Distinguished older Caucasian man, late 50s, silver hair, neat beard, "
        "wire-rimmed glasses, wearing a dark tweed jacket with leather elbow patches, "
        "warm brown eyes, university office background with bookshelves"
    ),
    "Dr Weaver": (
        "South Asian woman, mid 40s, long dark hair with a silver streak, "
        "warm smile, wearing a teal blouse and pearl earrings, "
        "modern office background with a world map and plants"
    ),
    "Max Results": (
        "Athletic Black man, mid 30s, short fade haircut, confident expression, "
        "wearing a crisp white shirt with rolled sleeves and slim navy tie, "
        "modern glass-walled boardroom background"
    ),
    "Zara Doubt": (
        "East Asian woman, early 30s, sharp bob cut, intense focused gaze, "
        "wearing a black turtleneck, minimal silver jewelry, "
        "minimalist studio background, dramatic lighting"
    ),
    "Dr Data": (
        "Middle Eastern man, early 40s, well-groomed short dark hair, "
        "reading glasses pushed up on forehead, friendly smile, "
        "wearing a lab coat over a blue button-down, laboratory setting"
    ),
    "Sage Perspective": (
        "Mixed-heritage woman, late 30s, curly auburn hair, warm open expression, "
        "wearing a colourful woven scarf over an earth-toned top, "
        "cosy library-café background with warm lighting"
    ),
}


def _build_portrait_prompt(actor_name: str, description: str, archetype: str | None) -> str:
    """Build a DALL-E prompt for a consistent professional headshot."""
    appearance = ACTOR_APPEARANCE.get(actor_name, "")
    if not appearance:
        # Generic fallback for unknown actors
        appearance = f"Professional person matching this description: {description}"

    return (
        f"Professional headshot portrait photograph. {appearance}. "
        f"Shot at f/2.8 with shallow depth of field. "
        f"Studio lighting, photorealistic, high resolution. "
        f"Neutral friendly expression, looking slightly off-camera. "
        f"No text, no watermarks, no logos."
    )


async def generate_portrait(
    actor_name: str,
    description: str,
    archetype: str | None = None,
    save_dir: Path | None = None,
) -> dict:
    """Generate a portrait using DALL-E 3 and return avatar_config dict.

    Returns:
        dict with portrait_url, portrait_prompt, and generation metadata.
        If save_dir is provided, also saves the image locally and includes local_path.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY required for portrait generation")

    prompt = _build_portrait_prompt(actor_name, description, archetype)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "hd",
                "response_format": "b64_json",
            },
        )
        response.raise_for_status()
        data = response.json()

    image_b64 = data["data"][0]["b64_json"]
    revised_prompt = data["data"][0].get("revised_prompt", prompt)

    result: dict = {
        "portrait_prompt": prompt,
        "revised_prompt": revised_prompt,
        "generated": True,
    }

    # Save locally if directory provided
    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{actor_name.lower().replace(' ', '_')}_portrait.png"
        filepath = save_dir / filename
        filepath.write_bytes(base64.b64decode(image_b64))
        result["local_path"] = str(filepath)
        result["portrait_url"] = f"/static/portraits/{filename}"
        logger.info("Saved portrait for %s to %s", actor_name, filepath)
    else:
        # Store as data URI (fallback — large but works without file serving)
        result["portrait_url"] = f"data:image/png;base64,{image_b64[:100]}..."
        result["portrait_data_b64"] = image_b64

    return result


async def generate_all_portraits(save_dir: Path | None = None) -> dict[str, dict]:
    """Generate portraits for all known actors.

    Returns dict mapping actor name → avatar_config.
    """
    results = {}
    for name in ACTOR_APPEARANCE:
        try:
            config = await generate_portrait(
                actor_name=name,
                description="",
                save_dir=save_dir,
            )
            results[name] = config
            logger.info("Generated portrait for %s", name)
        except Exception:
            logger.exception("Failed to generate portrait for %s", name)
    return results


# ── Flux.1 Dev via Replicate API ───────────────────────────────────────────


def _build_flux1_prompt(actor_name: str, description: str) -> str:
    """Build a Flux.1 portrait prompt (more descriptive works better)."""
    appearance = ACTOR_APPEARANCE.get(actor_name, "")
    if not appearance:
        appearance = f"Professional person matching: {description}"

    return (
        f"Professional headshot portrait photograph, studio lighting, "
        f"f/2.8 shallow depth of field, photorealistic, 8k resolution. "
        f"{appearance}. "
        f"Neutral friendly expression, looking slightly off-camera. "
        f"Clean background, no text, no watermarks."
    )


async def generate_portrait_flux1(
    actor_name: str,
    description: str,
    archetype: str | None = None,
    save_dir: Path | None = None,
) -> dict:
    """Generate a portrait using Flux.1 Dev via Replicate API.

    Returns dict with portrait_url, portrait_prompt, and generation metadata.
    """
    settings = get_settings()
    if not settings.replicate_api_token:
        raise RuntimeError("REPLICATE_API_TOKEN required for Flux.1 portrait generation")

    prompt = _build_flux1_prompt(actor_name, description)
    headers = {
        "Authorization": f"Bearer {settings.replicate_api_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Create prediction
        resp = await client.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json={
                "model": "black-forest-labs/flux-1.1-pro",
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": "1:1",
                    "output_format": "png",
                    "output_quality": 100,
                },
            },
        )
        resp.raise_for_status()
        prediction = resp.json()

        # Poll for completion (max ~2 min)
        poll_url = prediction["urls"]["get"]
        image_url: str | None = None
        for _ in range(60):
            await asyncio.sleep(2)
            poll_resp = await client.get(poll_url, headers=headers)
            poll_resp.raise_for_status()
            status = poll_resp.json()

            if status["status"] == "succeeded":
                output = status["output"]
                image_url = output[0] if isinstance(output, list) else output
                break
            elif status["status"] == "failed":
                raise RuntimeError(
                    f"Flux.1 generation failed: {status.get('error', 'unknown')}"
                )
        else:
            raise RuntimeError("Flux.1 generation timed out after 120s")

        # Download image
        img_resp = await client.get(image_url)
        img_resp.raise_for_status()
        image_bytes = img_resp.content

    result: dict = {
        "portrait_prompt": prompt,
        "portrait_source": "flux1",
        "generated": True,
    }

    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{actor_name.lower().replace(' ', '_')}_portrait.png"
        filepath = save_dir / filename
        filepath.write_bytes(image_bytes)
        result["local_path"] = str(filepath)
        result["portrait_url"] = f"/static/portraits/{filename}"
        logger.info("Saved Flux.1 portrait for %s to %s", actor_name, filepath)
    else:
        result["portrait_data_b64"] = base64.b64encode(image_bytes).decode()

    return result
