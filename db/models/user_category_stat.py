import uuid

from sqlalchemy import DateTime, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class UserCategoryStat(Base):
    __tablename__ = "user_category_stats"
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", name="uq_user_category_stats_user_category"),
        Index("idx_user_category_stats_user_id", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    last_used_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
