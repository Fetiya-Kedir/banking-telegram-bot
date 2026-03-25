from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.i18n.translator import t
from app.bot.keyboards.info import about_keyboard


def build_about_text(lang: str, bank_name: str) -> str:
    return (
        f"{t(lang, 'ABOUT_TITLE')}\n\n"
        f"{t(lang, 'ABOUT_BODY').format(bank_name=bank_name)}\n\n"
        f"{t(lang, 'ABOUT_WEBSITE_NOTE')}"
    )


async def show_about_screen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    lang: str,
) -> None:
    if update.callback_query is None:
        return

    settings = context.application.bot_data["settings"]

    await update.callback_query.edit_message_text(
        text=build_about_text(lang, settings.bank_name),
        reply_markup=about_keyboard(lang, settings.bank_website),
    )