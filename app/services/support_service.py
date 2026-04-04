from __future__ import annotations

from telegram import Bot, User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.repositories.support_repo import SupportRepository


def build_admin_ticket_message(
    *,
    ticket_code: str,
    telegram_user: TelegramUser,
    language_code_selected: str,
    question_text: str,
) -> str:
    username = f"@{telegram_user.username}" if telegram_user.username else "N/A"
    full_name = " ".join(
        part for part in [telegram_user.first_name, telegram_user.last_name] if part
    ).strip() or telegram_user.first_name or "Unknown User"

    return (
        f"🆕 Support Ticket {ticket_code}\n\n"
        f"👤 Name: {full_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 Telegram ID: {telegram_user.id}\n"
        f"🌐 Language: {language_code_selected}\n\n"
        f"💬 Question:\n{question_text}\n\n"
        f"Reply directly to this message to send your response back to the user."
    )


async def create_support_ticket_and_forward(
    *,
    session: AsyncSession,
    bot: Bot,
    admin_group_id: int,
    db_user: User,
    telegram_user: TelegramUser,
    question_text: str,
    language_code_selected: str,
):
    repo = SupportRepository(session)

    ticket = await repo.create_ticket(
        user_id=db_user.id,
        user_telegram_id=db_user.telegram_user_id,
        question_text=question_text,
        language_code_selected=language_code_selected,
    )

    admin_message = await bot.send_message(
        chat_id=admin_group_id,
        text=build_admin_ticket_message(
            ticket_code=ticket.ticket_code,
            telegram_user=telegram_user,
            language_code_selected=language_code_selected,
            question_text=question_text,
        ),
    )

    ticket = await repo.attach_admin_message(
        ticket,
        admin_chat_id=admin_group_id,
        admin_group_message_id=admin_message.message_id,
    )

    await repo.create_message_map(
        ticket_id=ticket.id,
        admin_chat_id=admin_group_id,
        admin_group_message_id=admin_message.message_id,
        user_telegram_id=db_user.telegram_user_id,
    )

    return ticket