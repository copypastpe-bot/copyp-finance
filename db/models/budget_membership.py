import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class BudgetMembership(Base):
    __tablename__ = "budget_memberships"
    __table_args__ = (
        UniqueConstraint("budget_id", "user_id", name="uq_budget_memberships_budget_user"),
        Index("idx_budget_memberships_budget_id", "budget_id"),
        Index("idx_budget_memberships_user_id", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("budgets.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    joined_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
