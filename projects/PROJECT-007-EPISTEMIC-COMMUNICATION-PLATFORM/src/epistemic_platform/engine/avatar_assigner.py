"""Auto-assign HeyGen stock avatars to actors based on persona characteristics.

Queries the HeyGen avatar library, scores each stock avatar against
persona traits (gender, age, appearance keywords), and assigns the
best unique match to each actor.

Runs at startup when avatar_mode == "heygen" and actors lack a heygen_avatar_id.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.engine.heygen_client import HeyGenClient
from epistemic_platform.models.actor_profile import ActorProfile

logger = logging.getLogger(__name__)


@dataclass
class PersonaTraits:
    """Desired avatar traits for matching."""

    gender: str  # "male" or "female"
    age_range: str  # "young", "middle", "mature"
    keywords: list[str]  # appearance/style keywords to match in avatar name/tags
    voice_tone: str  # for logging/debug


# Persona-to-trait mapping based on our 6 actors' established characteristics
ACTOR_PERSONA_TRAITS: dict[str, PersonaTraits] = {
    "Professor Axelrod": PersonaTraits(
        gender="male",
        age_range="mature",
        keywords=["professor", "academic", "formal", "suit", "glasses", "older", "mature"],
        voice_tone="authoritative, formal",
    ),
    "Dr Weaver": PersonaTraits(
        gender="female",
        age_range="middle",
        keywords=["professional", "warm", "mentor", "business", "smart", "friendly"],
        voice_tone="warm, approachable",
    ),
    "Max Results": PersonaTraits(
        gender="male",
        age_range="young",
        keywords=["business", "casual", "energetic", "confident", "shirt", "dynamic"],
        voice_tone="energetic, direct",
    ),
    "Zara Doubt": PersonaTraits(
        gender="female",
        age_range="young",
        keywords=["sharp", "professional", "analytical", "modern", "intense", "confident"],
        voice_tone="sharp, challenging",
    ),
    "Dr Data": PersonaTraits(
        gender="male",
        age_range="middle",
        keywords=["researcher", "scientist", "methodical", "glasses", "smart", "lab"],
        voice_tone="methodical, precise",
    ),
    "Sage Perspective": PersonaTraits(
        gender="female",
        age_range="mature",
        keywords=["wise", "calm", "inclusive", "warm", "gentle", "diverse"],
        voice_tone="calm, inclusive",
    ),
}


def _score_avatar(avatar: dict, traits: PersonaTraits) -> float:
    """Score a stock avatar against desired persona traits (0.0-1.0)."""
    score = 0.0
    avatar_name = (avatar.get("avatar_name") or "").lower()
    avatar_id = (avatar.get("avatar_id") or "").lower()
    gender = (avatar.get("gender") or "").lower()
    searchable = f"{avatar_name} {avatar_id}"

    # Gender match (most important)
    if gender == traits.gender:
        score += 0.5
    elif gender and gender != traits.gender:
        return 0.0  # Wrong gender — disqualify

    # Keyword matches in avatar name/id
    keyword_hits = sum(1 for kw in traits.keywords if kw in searchable)
    if keyword_hits > 0:
        score += min(0.3, keyword_hits * 0.1)

    # Age range heuristic from name
    age_keywords = {
        "young": ["young", "junior", "teen", "fresh"],
        "middle": ["professional", "business", "office"],
        "mature": ["mature", "senior", "elder", "professor", "old"],
    }
    for kw in age_keywords.get(traits.age_range, []):
        if kw in searchable:
            score += 0.1
            break

    # Slight boost for avatars with preview images (higher quality)
    if avatar.get("preview_url") or avatar.get("preview_image_url"):
        score += 0.05

    return min(1.0, score)


async def assign_heygen_avatars(db: AsyncSession) -> int:
    """Fetch HeyGen stock avatars and assign best matches to actors.

    Only assigns to actors that don't already have a heygen_avatar_id.
    Returns count of actors updated.
    """
    client = HeyGenClient()
    try:
        all_avatars = await client.list_avatars()
    except Exception as e:
        logger.warning("Cannot fetch HeyGen avatars (API key missing/invalid?): %s", e)
        return 0
    finally:
        await client.close()

    if not all_avatars:
        logger.warning("HeyGen returned 0 avatars — check API key permissions")
        return 0

    # Filter to stock/public avatars only (not custom/private)
    stock_avatars = [
        a for a in all_avatars
        if a.get("avatar_type", "").lower() in ("stock", "public", "")
        or not a.get("avatar_type")  # Some API versions don't include type
    ]

    if not stock_avatars:
        # Fall back to all avatars if none are explicitly "stock"
        stock_avatars = all_avatars

    logger.info("HeyGen: %d stock avatars available for matching", len(stock_avatars))

    # Load actors that need avatar assignment
    result = await db.execute(select(ActorProfile).where(ActorProfile.is_active.is_(True)))
    actors = result.scalars().all()

    used_avatar_ids: set[str] = set()
    updated = 0

    for actor in actors:
        # Skip if already assigned
        existing_config = actor.avatar_config or {}
        if existing_config.get("heygen_avatar_id"):
            used_avatar_ids.add(existing_config["heygen_avatar_id"])
            continue

        traits = ACTOR_PERSONA_TRAITS.get(actor.name)
        if not traits:
            logger.debug("No persona traits defined for actor '%s', skipping", actor.name)
            continue

        # Score all available stock avatars
        scored = [
            (a, _score_avatar(a, traits))
            for a in stock_avatars
            if a.get("avatar_id") not in used_avatar_ids
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        if not scored or scored[0][1] == 0.0:
            # No gender match — fall back to best available of correct gender
            # or just take highest-scored remaining
            gender_filtered = [
                (a, s) for a, s in scored if (a.get("gender") or "").lower() == traits.gender
            ]
            if gender_filtered:
                best_avatar, best_score = gender_filtered[0]
            elif scored:
                best_avatar, best_score = scored[0]
            else:
                logger.warning("No avatars left to assign to '%s'", actor.name)
                continue
        else:
            best_avatar, best_score = scored[0]

        avatar_id = best_avatar["avatar_id"]
        used_avatar_ids.add(avatar_id)

        # Update actor's avatar_config
        new_config = {
            **(actor.avatar_config or {}),
            "heygen_avatar_id": avatar_id,
            "heygen_avatar_name": best_avatar.get("avatar_name", ""),
            "heygen_preview_url": (
                best_avatar.get("preview_image_url")
                or best_avatar.get("preview_url")
                or ""
            ),
            "auto_assigned": True,
        }
        actor.avatar_config = new_config
        updated += 1

        logger.info(
            "Assigned HeyGen avatar '%s' (%s) to %s (score=%.2f, gender=%s)",
            best_avatar.get("avatar_name", avatar_id),
            avatar_id,
            actor.name,
            best_score,
            best_avatar.get("gender", "?"),
        )

    if updated:
        await db.commit()
        logger.info("Auto-assigned HeyGen avatars to %d actors", updated)

    return updated
