from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.i18n.translator import t
from app.bot.keyboards.support import support_confirmation_keyboard
from app.db.repositories.support_repo import SupportRepository
from app.services.user_service import get_user_language


def build_user_support_reply_text(
    lang: str,
    reply_text: str,
    ticket_code: str | None = None,
) -> str:
    lines = [t(lang, "SUPPORT_RESPONSE_TITLE"), ""]

    if ticket_code:
        lines.append(t(lang, "SUPPORT_RESPONSE_REFERENCE").format(ticket_code=ticket_code))
        lines.append("")

    lines.append(reply_text)
    return "\n".join(lines)


async def handle_admin_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.effective_chat is None:
        return

    if update.message.reply_to_message is None:
        return

    if not update.message.text:
        return

    if update.effective_user is None:
        return

    settings = context.application.bot_data["settings"]
    if update.effective_chat.id != settings.admin_group_id:
        return

    replied_message_id = update.message.reply_to_message.message_id
    admin_reply_text = update.message.text.strip()
    if not admin_reply_text:
        return

    session_factory = context.application.bot_data["session_factory"]

    async with session_factory() as session:
        repo = SupportRepository(session)

        mapping = await repo.get_message_map_by_admin_message(
            admin_chat_id=update.effective_chat.id,
            admin_group_message_id=replied_message_id,
        )

        if mapping is None:
            return

        lang = await get_user_language(
            session=session,
            telegram_user_id=mapping.user_telegram_id,
            default_language=settings.default_language,
        )

        ticket = await repo.get_ticket_by_id(mapping.ticket_id)
        ticket_code = ticket.ticket_code if ticket is not None else None

    sent_message = await context.bot.send_message(
        chat_id=mapping.user_telegram_id,
        text=build_user_support_reply_text(lang, admin_reply_text, ticket_code),
        reply_markup=support_confirmation_keyboard(lang),
    )

    admin_name = " ".join(
        part for part in [update.effective_user.first_name, update.effective_user.last_name] if part
    ).strip() or update.effective_user.first_name or "Unknown Admin"

    async with session_factory() as session:
        repo = SupportRepository(session)

        await repo.create_reply(
            ticket_id=mapping.ticket_id,
            admin_telegram_id=update.effective_user.id,
            admin_username=update.effective_user.username,
            admin_name=admin_name,
            reply_text=admin_reply_text,
            admin_group_chat_id=update.effective_chat.id,
            admin_group_message_id=update.message.message_id,
            sent_to_user_message_id=sent_message.message_id,
        )

        ticket = await repo.get_ticket_by_id(mapping.ticket_id)
        if ticket is not None:
            await repo.mark_ticket_answered(ticket)