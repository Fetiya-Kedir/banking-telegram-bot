from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SupportReply(Base):
    __tablename__ = "support_replies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    ticket_id: Mapped[int] = mapped_column(ForeignKey("support_tickets.id"), nullable=False, index=True)

    admin_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    admin_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    admin_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    reply_text: Mapped[str] = mapped_column(Text, nullable=False)

    admin_group_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    admin_group_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    sent_to_user_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )