import uuid

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import CHAR

from db.base import Base


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint(
            "(aux_currency_1 IS NULL OR aux_currency_1 <> base_currency) "
            "AND (aux_currency_2 IS NULL OR aux_currency_2 <> base_currency) "
            "AND (aux_currency_1 IS NULL OR aux_currency_2 IS NULL OR aux_currency_1 <> aux_currency_2)",
            name="chk_budget_aux_distinct",
        ),
        Index("idx_budgets_created_by_user_id", "created_by_user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    base_currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    aux_currency_1: Mapped[str | None] = mapped_column(CHAR(3), nullable=True)
    aux_currency_2: Mapped[str | None] = mapped_column(CHAR(3), nullable=True)
    timezone: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
