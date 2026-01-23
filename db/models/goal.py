import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (
        Index("idx_goals_budget_id", "budget_id"),
        Index("idx_goals_owner_user_id", "owner_user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("budgets.id"), nullable=False)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    visibility: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    target_amount_base: Mapped[Numeric | None] = mapped_column(Numeric(14, 2), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
