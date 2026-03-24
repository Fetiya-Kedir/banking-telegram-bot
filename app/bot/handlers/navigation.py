from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.atm import clear_atm_state
from app.bot.handlers.branch import clear_branch_state
from app.bot.handlers.menu import build_main_menu_text
from app.bot.i18n.translator import t
from app.bot.keyboards.language import language_keyboard
from app.bot.keyboards.menu import main_menu_keyboard
from app.config.constants import NAV_CHANGE_LANGUAGE, NAV_HOME
from app.services.user_service import get_user_language


async def handle_navigation_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.callback_query is None or update.effective_user is None:
        return

    query = update.callback_query
    await query.answer()

    clear_branch_state(context)
    clear_atm_state(context)

    settings = context.application.bot_data["settings"]
    session_factory = context.application.bot_data["session_factory"]

    async with session_factory() as session:
        lang = await get_user_language(
            session=session,
            telegram_user_id=update.effective_user.id,
            default_language=settings.default_language,
        )

    raw_data = query.data or ""
    _, action = raw_data.split(":", maxsplit=1)

    if action == NAV_CHANGE_LANGUAGE:
        await query.edit_message_text(
            text=t(lang, "LANGUAGE_PROMPT"),
            reply_markup=language_keyboard(),
        )
        return

    if action == NAV_HOME:
        display_name = update.effective_user.first_name or "there"
        await query.edit_message_text(
            text=build_main_menu_text(lang, display_name),
            reply_markup=main_menu_keyboard(lang),
        )
        return