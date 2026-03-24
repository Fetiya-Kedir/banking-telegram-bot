from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.atm import clear_atm_state, show_atm_menu_screen
from app.bot.handlers.branch import clear_branch_state, show_branch_menu_screen
from app.bot.handlers.faq import show_faq_categories_screen
from app.bot.i18n.translator import t
from app.bot.keyboards.menu import main_menu_keyboard
from app.config.constants import (
    MENU_ABOUT,
    MENU_ATM,
    MENU_BRANCH,
    MENU_CONTACT,
    MENU_FAQ,
    MENU_SUPPORT,
)
from app.services.user_service import get_user_language


MENU_RESPONSE_KEYS = {
    MENU_SUPPORT: "FEATURE_SUPPORT_PLACEHOLDER",
    MENU_ABOUT: "FEATURE_ABOUT_PLACEHOLDER",
    MENU_CONTACT: "FEATURE_CONTACT_PLACEHOLDER",
}


def build_main_menu_text(lang: str, display_name: str) -> str:
    return (
        f"{t(lang, 'WELCOME_MAIN_MENU').format(name=display_name)}\n\n"
        f"{t(lang, 'MAIN_MENU_PROMPT')}"
    )


async def handle_menu_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.callback_query is None or update.effective_user is None:
        return

    query = update.callback_query
    await query.answer()

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

    clear_branch_state(context)
    clear_atm_state(context)

    if action == MENU_FAQ:
        await show_faq_categories_screen(update, context, lang=lang)
        return

    if action == MENU_BRANCH:
        await show_branch_menu_screen(update, context, lang=lang)
        return

    if action == MENU_ATM:
        await show_atm_menu_screen(update, context, lang=lang)
        return

    response_key = MENU_RESPONSE_KEYS.get(action, "UNKNOWN_ACTION")

    await query.edit_message_text(
        text=t(lang, response_key),
        reply_markup=main_menu_keyboard(lang),
    )