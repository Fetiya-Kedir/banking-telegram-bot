from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SupportMessageMap(Base):
    __tablename__ = "support_message_maps"
    __table_args__ = (
        UniqueConstraint("admin_chat_id", "admin_group_message_id", name="uq_support_admin_message"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    ticket_id: Mapped[int] = mapped_column(ForeignKey("support_tickets.id"), nullable=False)

    admin_chat_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    admin_group_message_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    user_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )