from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.support_message_map import SupportMessageMap
from app.db.models.support_reply import SupportReply
from app.db.models.support_ticket import SupportTicket


def format_ticket_code(ticket_id: int) -> str:
    return f"TKT-ZZB-{ticket_id:05d}"


class SupportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_ticket(
        self,
        *,
        user_id: int,
        user_telegram_id: int,
        question_text: str,
        language_code_selected: str,
    ) -> SupportTicket:
        # Keep the temporary code safely under varchar(32)
        temporary_code = f"TMP-{uuid4().hex[:12].upper()}"

        ticket = SupportTicket(
            ticket_code=temporary_code,
            user_id=user_id,
            user_telegram_id=user_telegram_id,
            question_text=question_text,
            language_code_selected=language_code_selected,
            status="open",
        )
        self.session.add(ticket)
        await self.session.flush()

        ticket.ticket_code = format_ticket_code(ticket.id)

        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

    async def attach_admin_message(
        self,
        ticket: SupportTicket,
        *,
        admin_chat_id: int,
        admin_group_message_id: int,
    ) -> SupportTicket:
        ticket.admin_chat_id = admin_chat_id
        ticket.admin_group_message_id = admin_group_message_id
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

    async def create_message_map(
        self,
        *,
        ticket_id: int,
        admin_chat_id: int,
        admin_group_message_id: int,
        user_telegram_id: int,
    ) -> SupportMessageMap:
        mapping = SupportMessageMap(
            ticket_id=ticket_id,
            admin_chat_id=admin_chat_id,
            admin_group_message_id=admin_group_message_id,
            user_telegram_id=user_telegram_id,
        )
        self.session.add(mapping)
        await self.session.commit()
        await self.session.refresh(mapping)
        return mapping

    async def get_message_map_by_admin_message(
        self,
        *,
        admin_chat_id: int,
        admin_group_message_id: int,
    ) -> SupportMessageMap | None:
        stmt = select(SupportMessageMap).where(
            SupportMessageMap.admin_chat_id == admin_chat_id,
            SupportMessageMap.admin_group_message_id == admin_group_message_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_ticket_by_id(self, ticket_id: int) -> SupportTicket | None:
        stmt = select(SupportTicket).where(SupportTicket.id == ticket_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_ticket_answered(self, ticket: SupportTicket) -> SupportTicket:
        ticket.mark_answered()
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

    async def create_reply(
        self,
        *,
        ticket_id: int,
        admin_telegram_id: int,
        admin_username: str | None,
        admin_name: str | None,
        reply_text: str,
        admin_group_chat_id: int,
        admin_group_message_id: int,
        sent_to_user_message_id: int | None,
    ) -> SupportReply:
        reply = SupportReply(
            ticket_id=ticket_id,
            admin_telegram_id=admin_telegram_id,
            admin_username=admin_username,
            admin_name=admin_name,
            reply_text=reply_text,
            admin_group_chat_id=admin_group_chat_id,
            admin_group_message_id=admin_group_message_id,
            sent_to_user_message_id=sent_to_user_message_id,
        )
        self.session.add(reply)
        await self.session.commit()
        await self.session.refresh(reply)
        return reply
