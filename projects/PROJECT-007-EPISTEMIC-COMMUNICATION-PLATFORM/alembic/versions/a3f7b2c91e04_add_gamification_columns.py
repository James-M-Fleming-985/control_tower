"""add gamification columns to user_profiles

Revision ID: a3f7b2c91e04
Revises: d842c1e0030d
Create Date: 2026-03-22 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f7b2c91e04'
down_revision: Union[str, None] = 'd842c1e0030d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("xp", sa.Integer, nullable=False, server_default="0"))
    op.add_column("user_profiles", sa.Column("level", sa.Integer, nullable=False, server_default="1"))
    op.add_column("user_profiles", sa.Column("achievements", sa.JSON, nullable=False, server_default="[]"))
    op.add_column("user_profiles", sa.Column("subscription_tier", sa.String(20), nullable=False, server_default="free"))


def downgrade() -> None:
    op.drop_column("user_profiles", "subscription_tier")
    op.drop_column("user_profiles", "achievements")
    op.drop_column("user_profiles", "level")
    op.drop_column("user_profiles", "xp")
