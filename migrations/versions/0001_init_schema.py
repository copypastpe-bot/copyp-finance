"""init schema

Revision ID: 0001_init_schema
Revises:
Create Date: 2026-01-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0001_init_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_username", sa.Text(), nullable=True),
        sa.Column("first_name", sa.Text(), nullable=True),
        sa.Column("last_name", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_user_id", name="uq_users_telegram_user_id"),
    )

    op.create_table(
        "budgets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("base_currency", sa.CHAR(length=3), nullable=False),
        sa.Column("aux_currency_1", sa.CHAR(length=3), nullable=True),
        sa.Column("aux_currency_2", sa.CHAR(length=3), nullable=True),
        sa.Column("timezone", sa.Text(), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_archived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.CheckConstraint(
            "(aux_currency_1 IS NULL OR aux_currency_1 <> base_currency) "
            "AND (aux_currency_2 IS NULL OR aux_currency_2 <> base_currency) "
            "AND (aux_currency_1 IS NULL OR aux_currency_2 IS NULL OR aux_currency_1 <> aux_currency_2)",
            name="chk_budget_aux_distinct",
        ),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_budgets_created_by_user_id", "budgets", ["created_by_user_id"], unique=False)

    op.create_table(
        "budget_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("budget_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.ForeignKeyConstraint(["budget_id"], ["budgets.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("budget_id", "user_id", name="uq_budget_memberships_budget_user"),
    )
    op.create_index("idx_budget_memberships_budget_id", "budget_memberships", ["budget_id"], unique=False)
    op.create_index("idx_budget_memberships_user_id", "budget_memberships", ["user_id"], unique=False)

    op.create_table(
        "budget_counters",
        sa.Column("budget_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("next_seq_no", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["budget_id"], ["budgets.id"]),
        sa.PrimaryKeyConstraint("budget_id"),
    )

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("budget_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.ForeignKeyConstraint(["budget_id"], ["budgets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("budget_id", "name", "kind", name="uq_categories_budget_name_kind"),
    )
    op.create_index("idx_categories_budget_id", "categories", ["budget_id"], unique=False)

    op.create_table(
        "user_category_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usage_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "category_id", name="uq_user_category_stats_user_category"),
    )
    op.create_index("idx_user_category_stats_user_id", "user_category_stats", ["user_id"], unique=False)

    op.create_table(
        "goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("budget_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("visibility", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("target_amount_base", sa.Numeric(14, 2), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_archived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.ForeignKeyConstraint(["budget_id"], ["budgets.id"]),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_goals_budget_id", "goals", ["budget_id"], unique=False)
    op.create_index("idx_goals_owner_user_id", "goals", ["owner_user_id"], unique=False)

    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("budget_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seq_no", sa.Integer(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.CHAR(length=3), nullable=False),
        sa.Column("amount_base", sa.Numeric(14, 2), nullable=False),
        sa.Column("fx_rate", sa.Numeric(18, 8), nullable=False),
        sa.Column("fx_date", sa.Date(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("deleted_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("input_type", sa.Text(), nullable=True),
        sa.Column("telegram_file_id", sa.Text(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("parsed_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint(
            "(type IN ('goal_deposit', 'goal_withdraw') AND goal_id IS NOT NULL) "
            "OR (type NOT IN ('goal_deposit', 'goal_withdraw') AND goal_id IS NULL)",
            name="chk_transactions_goal_type",
        ),
        sa.ForeignKeyConstraint(["budget_id"], ["budgets.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["deleted_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"]),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("budget_id", "seq_no", name="uq_transactions_budget_seq_no"),
    )
    op.create_index("idx_transactions_budget_id_local_date", "transactions", ["budget_id", "local_date"], unique=False)
    op.create_index("idx_transactions_budget_id_occurred_at", "transactions", ["budget_id", "occurred_at"], unique=False)
    op.create_index("idx_transactions_created_by_user_id", "transactions", ["created_by_user_id"], unique=False)
    op.create_index("idx_transactions_category_id", "transactions", ["category_id"], unique=False)

    op.create_table(
        "transaction_audit",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("edited_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("edited_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("before", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("after", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["edited_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_transaction_audit_transaction_id", "transaction_audit", ["transaction_id"], unique=False)
    op.create_index(
        "idx_transaction_audit_edited_by_user_id",
        "transaction_audit",
        ["edited_by_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_transaction_audit_edited_by_user_id", table_name="transaction_audit")
    op.drop_index("idx_transaction_audit_transaction_id", table_name="transaction_audit")
    op.drop_table("transaction_audit")

    op.drop_index("idx_transactions_category_id", table_name="transactions")
    op.drop_index("idx_transactions_created_by_user_id", table_name="transactions")
    op.drop_index("idx_transactions_budget_id_occurred_at", table_name="transactions")
    op.drop_index("idx_transactions_budget_id_local_date", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("idx_goals_owner_user_id", table_name="goals")
    op.drop_index("idx_goals_budget_id", table_name="goals")
    op.drop_table("goals")

    op.drop_index("idx_user_category_stats_user_id", table_name="user_category_stats")
    op.drop_table("user_category_stats")

    op.drop_index("idx_categories_budget_id", table_name="categories")
    op.drop_table("categories")

    op.drop_table("budget_counters")

    op.drop_index("idx_budget_memberships_user_id", table_name="budget_memberships")
    op.drop_index("idx_budget_memberships_budget_id", table_name="budget_memberships")
    op.drop_table("budget_memberships")

    op.drop_index("idx_budgets_created_by_user_id", table_name="budgets")
    op.drop_table("budgets")

    op.drop_table("users")
