#!/usr/bin/env python3
"""Seed data loader — loads seed actors and sample scenarios into the database.

Usage:
    python -m scripts.seed_data          # from the PROJECT-007 root
    python scripts/seed_data.py          # direct execution

Requires DATABASE_URL environment variable or .env file.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

# Ensure the src package is importable when running directly
_project_root = Path(__file__).resolve().parent.parent
_src_dir = _project_root / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from sqlalchemy import select

from epistemic_platform.database import async_session_factory, engine, Base
from epistemic_platform.models.actor_profile import ActorProfile
from epistemic_platform.models.scenario_definition import ScenarioDefinition

# Import models so Base.metadata is complete
from epistemic_platform.models import (  # noqa: F401
    actor_profile,
    user_profile,
    conversation_session,
    scenario_definition,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SEED_ACTORS_FILE = _src_dir / "epistemic_platform" / "ontology" / "seed_actors.json"

# Sample scenarios covering 3 categories x 2 difficulties for M1
SEED_SCENARIOS = [
    {
        "title": "The Budget Debate",
        "description": (
            "Your team has a limited budget and must choose between investing in "
            "a new product line or improving the existing one. Present your position "
            "and defend it against the actor's challenges."
        ),
        "difficulty": "beginner",
        "category": "workplace_negotiation",
        "objectives": [
            "State your position clearly with supporting reasons",
            "Respond to at least 3 counter-arguments",
            "Acknowledge the strengths of the opposing view",
        ],
        "evaluation_criteria": [
            "Clarity of initial position statement",
            "Quality of evidence provided",
            "Ability to address counterarguments without abandoning position",
        ],
    },
    {
        "title": "The Promotion Case",
        "description": (
            "You need to justify why you deserve a promotion to a sceptical manager "
            "who values concrete evidence over self-promotion. Build your case "
            "systematically."
        ),
        "difficulty": "intermediate",
        "category": "workplace_negotiation",
        "objectives": [
            "Present measurable accomplishments",
            "Connect past performance to future potential",
            "Handle tough questions about weaknesses or gaps",
        ],
        "evaluation_criteria": [
            "Evidence-based argumentation",
            "Handling of uncomfortable challenges",
            "Maintaining composure under pressure",
        ],
    },
    {
        "title": "Is AI Conscious?",
        "description": (
            "Engage in a philosophical debate about whether artificial intelligence "
            "can be truly conscious. You may take any position — the actor will "
            "challenge your reasoning from their epistemological stance."
        ),
        "difficulty": "intermediate",
        "category": "academic_debate",
        "objectives": [
            "Define your key terms (consciousness, intelligence, awareness)",
            "Provide at least 2 distinct arguments for your position",
            "Engage with the actor's philosophical framework",
        ],
        "evaluation_criteria": [
            "Conceptual clarity and precision",
            "Depth of philosophical engagement",
            "Ability to navigate the trilemma of justification",
        ],
    },
    {
        "title": "The Ethics of Mandatory Vaccination",
        "description": (
            "A challenging debate on balancing individual liberty with public health. "
            "The actor will probe the foundations of your ethical reasoning."
        ),
        "difficulty": "advanced",
        "category": "academic_debate",
        "objectives": [
            "Articulate your ethical framework explicitly",
            "Address tensions between competing values",
            "Respond to edge cases and thought experiments",
        ],
        "evaluation_criteria": [
            "Ethical framework coherence",
            "Handling of value trade-offs",
            "Resistance to reductio ad absurdum challenges",
        ],
    },
    {
        "title": "Breaking Bad News",
        "description": (
            "You need to tell a close friend that you can't attend their wedding. "
            "The actor plays the friend, reacting emotionally. Navigate the conversation "
            "with empathy while being honest."
        ),
        "difficulty": "beginner",
        "category": "interpersonal_conflict",
        "objectives": [
            "Communicate your situation honestly",
            "Acknowledge and validate the friend's feelings",
            "Propose a constructive alternative",
        ],
        "evaluation_criteria": [
            "Emotional intelligence and empathy",
            "Honesty without cruelty",
            "Solution-oriented communication",
        ],
    },
    {
        "title": "The Betrayal Confrontation",
        "description": (
            "You've discovered that a trusted colleague shared your confidential idea "
            "with management and took credit for it. Confront them directly."
        ),
        "difficulty": "advanced",
        "category": "interpersonal_conflict",
        "objectives": [
            "State the specific facts without exaggeration",
            "Express your feelings using 'I' statements",
            "Seek resolution rather than revenge",
        ],
        "evaluation_criteria": [
            "Precision of factual claims",
            "Emotional regulation under provocation",
            "Ability to navigate from confrontation to resolution",
        ],
    },
]


async def seed_all() -> None:
    """Create tables and seed actors + scenarios."""
    # Create tables if needed
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # Seed actors
        result = await db.execute(select(ActorProfile).limit(1))
        if result.scalar_one_or_none() is None:
            logger.info("Seeding actors from %s", SEED_ACTORS_FILE.name)
            with open(SEED_ACTORS_FILE) as f:
                actors_data = json.load(f)
            for data in actors_data:
                db.add(ActorProfile(**data))
            await db.flush()
            logger.info("  Created %d actors", len(actors_data))
        else:
            logger.info("Actors already exist, skipping")

        # Seed scenarios
        result = await db.execute(select(ScenarioDefinition).limit(1))
        if result.scalar_one_or_none() is None:
            logger.info("Seeding %d sample scenarios", len(SEED_SCENARIOS))
            for data in SEED_SCENARIOS:
                db.add(ScenarioDefinition(**data))
            await db.flush()
            logger.info("  Created %d scenarios", len(SEED_SCENARIOS))
        else:
            logger.info("Scenarios already exist, skipping")

        await db.commit()
        logger.info("Seed data complete")


def main() -> None:
    asyncio.run(seed_all())


if __name__ == "__main__":
    main()
