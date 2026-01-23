import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class BudgetCounter(Base):
    __tablename__ = "budget_counters"

    budget_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("budgets.id"),
        primary_key=True,
    )
    next_seq_no: Mapped[int] = mapped_column(Integer, server_default="1", nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
