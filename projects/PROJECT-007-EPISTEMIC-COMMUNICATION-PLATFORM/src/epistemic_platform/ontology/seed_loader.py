"""Seed loader — loads seed_actors.json and seed_scenarios.json into the database."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.models.actor_profile import ActorProfile
from epistemic_platform.models.scenario_definition import ScenarioDefinition


SEED_ACTORS_FILE = Path(__file__).parent / "seed_actors.json"
SEED_SCENARIOS_FILE = Path(__file__).parent / "seed_scenarios.json"


async def load_seed_actors(db: AsyncSession) -> list[ActorProfile]:
    """Load seed actors into DB if no actors exist yet. Returns created actors."""
    result = await db.execute(select(ActorProfile).limit(1))
    if result.scalar_one_or_none() is not None:
        return []  # Already seeded

    with open(SEED_ACTORS_FILE) as f:
        actors_data = json.load(f)

    created = []
    for data in actors_data:
        actor = ActorProfile(**data)
        db.add(actor)
        created.append(actor)

    await db.flush()
    return created


async def load_seed_scenarios(db: AsyncSession) -> list[ScenarioDefinition]:
    """Load seed scenarios into DB if no scenarios exist yet."""
    result = await db.execute(select(ScenarioDefinition).limit(1))
    if result.scalar_one_or_none() is not None:
        return []  # Already seeded

    with open(SEED_SCENARIOS_FILE) as f:
        scenarios_data = json.load(f)

    created = []
    for data in scenarios_data:
        scenario = ScenarioDefinition(**data)
        db.add(scenario)
        created.append(scenario)

    await db.flush()
    return created
