import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import CHAR

from db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("budget_id", "seq_no", name="uq_transactions_budget_seq_no"),
        CheckConstraint(
            "(type IN ('goal_deposit', 'goal_withdraw') AND goal_id IS NOT NULL) "
            "OR (type NOT IN ('goal_deposit', 'goal_withdraw') AND goal_id IS NULL)",
            name="chk_transactions_goal_type",
        ),
        Index("idx_transactions_budget_id_local_date", "budget_id", "local_date"),
        Index("idx_transactions_budget_id_occurred_at", "budget_id", "occurred_at"),
        Index("idx_transactions_created_by_user_id", "created_by_user_id"),
        Index("idx_transactions_category_id", "category_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("budgets.id"), nullable=False)
    seq_no: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    amount_base: Mapped[Numeric] = mapped_column(Numeric(14, 2), nullable=False)
    fx_rate: Mapped[Numeric] = mapped_column(Numeric(18, 8), nullable=False)
    fx_date: Mapped[Date] = mapped_column(Date, nullable=False)
    occurred_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    local_date: Mapped[Date] = mapped_column(Date, nullable=False)
    category_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    goal_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    deleted_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    input_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    telegram_file_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
