"""add role column to user_profiles

Revision ID: e1a2b3c4d5f6
Revises: c7d4e9f23b18
Create Date: 2026-03-24 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1a2b3c4d5f6"
down_revision: Union[str, None] = "c7d4e9f23b18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
    )
    # Make existing users admin (development convenience)
    op.execute("UPDATE user_profiles SET role = 'admin'")


def downgrade() -> None:
    op.drop_column("user_profiles", "role")
