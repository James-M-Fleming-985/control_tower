"""add syllabus column to user_profiles

Revision ID: f8a3c5d72e19
Revises: b5e8d3f12a07
Create Date: 2026-03-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a3c5d72e19'
down_revision: Union[str, None] = 'e1a2b3c4d5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    if not _has_column("user_profiles", "syllabus"):
        op.add_column(
            "user_profiles",
            sa.Column("syllabus", sa.JSON, nullable=False, server_default="{}"),
        )

    # Hard reset legacy gamification data — single-user platform, fresh start
    op.execute(
        sa.text(
            "UPDATE user_profiles SET xp = 0, level = 1, achievements = '[]'::jsonb, syllabus = '{}'::jsonb"
        )
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "syllabus")
