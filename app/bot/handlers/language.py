from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.atm import clear_atm_state
from app.bot.handlers.branch import clear_branch_state
from app.bot.handlers.menu import build_main_menu_text
from app.bot.keyboards.menu import main_menu_keyboard
from app.config.constants import SUPPORTED_LANGUAGES
from app.services.user_service import set_user_language

logger = logging.getLogger(__name__)


async def handle_language_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.callback_query is None or update.effective_user is None:
        return

    query = update.callback_query
    await query.answer()

    clear_branch_state(context)
    clear_atm_state(context)

    raw_data = query.data or ""
    _, selected_language = raw_data.split(":", maxsplit=1)

    if selected_language not in SUPPORTED_LANGUAGES:
        return

    session_factory = context.application.bot_data["session_factory"]

    async with session_factory() as session:
        user = await set_user_language(
            session=session,
            telegram_user_id=update.effective_user.id,
            language_code_selected=selected_language,
        )

    logger.info(
        "User %s selected language %s.",
        update.effective_user.id,
        selected_language,
    )

    display_name = (
        user.first_name
        if user is not None and user.first_name
        else update.effective_user.first_name or "there"
    )

    await query.edit_message_text(
        text=build_main_menu_text(selected_language, display_name),
        reply_markup=main_menu_keyboard(selected_language),
    )