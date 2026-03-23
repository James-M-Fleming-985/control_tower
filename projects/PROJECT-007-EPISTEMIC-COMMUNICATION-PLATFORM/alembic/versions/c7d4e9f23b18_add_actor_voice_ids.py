"""add voice_id to actor ontology_config

Revision ID: c7d4e9f23b18
Revises: b5e8d3f12a07
Create Date: 2026-03-23 10:00:00.000000

"""
import json
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = "c7d4e9f23b18"
down_revision: Union[str, None] = "b5e8d3f12a07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ElevenLabs pre-made voice IDs per actor
VOICE_MAP = {
    "Professor Axelrod": "VR6AewLTigWG4xSOukaG",
    "Dr Weaver": "21m00Tcm4TlvDq8ikWAM",
    "Max Results": "TxGEqnHWrfWFTfGW9XjX",
    "Zara Doubt": "AZnzlk1XvdvUeBnXmlld",
    "Dr Data": "ErXwobaYiN019PkySvjV",
    "Sage Perspective": "EXAVITQu4vr4xnSDxMaL",
}


def upgrade() -> None:
    conn = op.get_bind()
    for name, voice_id in VOICE_MAP.items():
        row = conn.execute(
            text("SELECT id, ontology_config FROM actor_profiles WHERE name = :name"),
            {"name": name},
        ).fetchone()
        if not row:
            continue
        config = row[1] if isinstance(row[1], dict) else json.loads(row[1] or "{}")
        config["voice_id"] = voice_id
        conn.execute(
            text("UPDATE actor_profiles SET ontology_config = :config WHERE id = :id"),
            {"config": json.dumps(config), "id": row[0]},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for name in VOICE_MAP:
        row = conn.execute(
            text("SELECT id, ontology_config FROM actor_profiles WHERE name = :name"),
            {"name": name},
        ).fetchone()
        if not row:
            continue
        config = row[1] if isinstance(row[1], dict) else json.loads(row[1] or "{}")
        config.pop("voice_id", None)
        conn.execute(
            text("UPDATE actor_profiles SET ontology_config = :config WHERE id = :id"),
            {"config": json.dumps(config), "id": row[0]},
        )
