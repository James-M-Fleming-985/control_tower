"""add parent_session_id to conversation_sessions

Revision ID: b5e8d3f12a07
Revises: a3f7b2c91e04
Create Date: 2026-03-22 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5e8d3f12a07'
down_revision: Union[str, None] = 'a3f7b2c91e04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    if not _has_column("conversation_sessions", "parent_session_id"):
        op.add_column(
            "conversation_sessions",
            sa.Column("parent_session_id", sa.Integer, sa.ForeignKey("conversation_sessions.id"), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("conversation_sessions", "parent_session_id")
