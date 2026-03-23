"""initial_schema

Revision ID: d842c1e0030d
Revises: 
Create Date: 2026-03-11 15:42:04.719920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd842c1e0030d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return name in insp.get_table_names()


def upgrade() -> None:
    if not _table_exists("actor_profiles"):
      op.create_table(
        "actor_profiles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("epistemological_stance", sa.String(50), nullable=False, index=True),
        sa.Column("ontology_config", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("archetype", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("avatar_config", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
      )

    if not _table_exists("user_profiles"):
      op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("skill_level", sa.String(50), nullable=False, server_default="beginner"),
        sa.Column("assessment_history", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("preferences", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
      )

    if not _table_exists("scenario_definitions"):
      op.create_table(
        "scenario_definitions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=False, index=True),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("actor_profiles.id"), nullable=True),
        sa.Column("objectives", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("evaluation_criteria", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
      )

    if not _table_exists("conversation_sessions"):
      op.create_table(
        "conversation_sessions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("user_profiles.id"), nullable=False),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("actor_profiles.id"), nullable=False),
        sa.Column("scenario_id", sa.Integer, sa.ForeignKey("scenario_definitions.id"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("mode", sa.String(10), nullable=False, server_default="text"),
        sa.Column("messages", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("coaching_annotations", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("trilemma_state", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("turn_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
      )


def downgrade() -> None:
    op.drop_table("conversation_sessions")
    op.drop_table("scenario_definitions")
    op.drop_table("user_profiles")
    op.drop_table("actor_profiles")
