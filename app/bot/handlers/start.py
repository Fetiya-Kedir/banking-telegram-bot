from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards.language import language_keyboard
from app.services.user_service import upsert_telegram_user

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None or update.message is None:
        return

    settings = context.application.bot_data["settings"]
    session_factory = context.application.bot_data["session_factory"]

    async with session_factory() as session:
        user = await upsert_telegram_user(
            session=session,
            telegram_user=update.effective_user,
            default_language=settings.default_language,
        )

    display_name = user.first_name or update.effective_user.first_name or "there"

    logger.info("User %s started the bot.", user.telegram_user_id)

    text = (
        f"Hello, {display_name}!\n\n"
        "Please choose your language / ቋንቋ ይምረጡ / Afaan filadhu:"
    )

    await update.message.reply_text(
        text=text,
        reply_markup=language_keyboard(),
    )