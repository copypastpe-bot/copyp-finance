"""add budget invites

Revision ID: 0002_add_budget_invites
Revises: 0001_init_schema
Create Date: 2026-01-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0002_add_budget_invites"
down_revision: Union[str, None] = "0001_init_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "budget_invites",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("budget_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.Text(), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("max_uses", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("used_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.ForeignKeyConstraint(["budget_id"], ["budgets.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ux_budget_invites_token", "budget_invites", ["token"], unique=True)
    op.create_index("idx_budget_invites_budget_id", "budget_invites", ["budget_id"], unique=False)
    op.create_index(
        "idx_budget_invites_created_by_user_id",
        "budget_invites",
        ["created_by_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_budget_invites_created_by_user_id", table_name="budget_invites")
    op.drop_index("idx_budget_invites_budget_id", table_name="budget_invites")
    op.drop_index("ux_budget_invites_token", table_name="budget_invites")
    op.drop_table("budget_invites")
