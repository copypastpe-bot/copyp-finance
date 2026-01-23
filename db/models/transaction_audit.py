import uuid

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class TransactionAudit(Base):
    __tablename__ = "transaction_audit"
    __table_args__ = (
        Index("idx_transaction_audit_transaction_id", "transaction_id"),
        Index("idx_transaction_audit_edited_by_user_id", "edited_by_user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id"),
        nullable=False,
    )
    edited_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    edited_by_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    before: Mapped[dict] = mapped_column(JSONB, nullable=False)
    after: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
