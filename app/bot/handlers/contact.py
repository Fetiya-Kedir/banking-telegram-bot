from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.i18n.translator import t
from app.bot.keyboards.info import contact_keyboard


def build_contact_text(
    lang: str,
    *,
    bank_name: str,
    phone: str | None,
    email: str | None,
) -> str:
    lines = [
        f"{t(lang, 'CONTACT_TITLE')}",
        "",
        f"{bank_name}",
        "",
        t(lang, "CONTACT_BODY"),
    ]

    if phone:
        lines.append("")
        lines.append(f"{t(lang, 'CONTACT_PHONE_LABEL')}: {phone}")

    if email:
        lines.append(f"{t(lang, 'CONTACT_EMAIL_LABEL')}: {email}")

    return "\n".join(lines)


async def show_contact_screen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    lang: str,
) -> None:
    if update.callback_query is None:
        return

    settings = context.application.bot_data["settings"]

    await update.callback_query.edit_message_text(
        text=build_contact_text(
            lang,
            bank_name=settings.bank_name,
            phone=settings.bank_phone,
            email=settings.bank_support_email,
        ),
        reply_markup=contact_keyboard(
            lang,
            website_url=settings.bank_website,
            telegram_url=settings.bank_telegram_url,
            facebook_url=settings.bank_facebook_url,
            instagram_url=settings.bank_instagram_url,
            tiktok_url=settings.bank_tiktok_url,
            youtube_url=settings.bank_youtube_url,
            linkedin_url=settings.bank_linkedin_url,
            phone=settings.bank_phone,
            email=settings.bank_support_email,
        ),
    )