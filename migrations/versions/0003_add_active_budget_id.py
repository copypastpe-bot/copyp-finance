"""add active budget id

Revision ID: 0003_add_active_budget_id
Revises: 0002_add_budget_invites
Create Date: 2026-01-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_add_active_budget_id"
down_revision: Union[str, None] = "0002_add_budget_invites"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("active_budget_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_users_active_budget_id",
        "users",
        "budgets",
        ["active_budget_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_active_budget_id", "users", type_="foreignkey")
    op.drop_column("users", "active_budget_id")
