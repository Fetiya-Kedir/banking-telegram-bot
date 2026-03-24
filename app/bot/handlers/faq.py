from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.i18n.translator import t
from app.bot.keyboards.faq import (
    faq_answer_keyboard,
    faq_categories_keyboard,
    faq_questions_keyboard,
)
from app.services.faq_service import get_all_categories, get_category_by_id, get_item_by_id
from app.services.user_service import get_user_language


def build_faq_categories_text(lang: str) -> str:
    return (
        f"{t(lang, 'FAQ_CATEGORIES_TITLE')}\n\n"
        f"{t(lang, 'FAQ_CATEGORIES_PROMPT')}"
    )


def build_faq_questions_text(lang: str, category_title: str) -> str:
    return (
        f"{category_title}\n\n"
        f"{t(lang, 'FAQ_QUESTIONS_PROMPT')}"
    )


def build_faq_answer_text(lang: str, question: str, answer: str) -> str:
    return (
        f"❓ {question}\n\n"
        f"💡 {t(lang, 'FAQ_ANSWER_TITLE')}\n"
        f"{answer}"
    )


async def show_faq_categories_screen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    lang: str,
) -> None:
    if update.callback_query is None:
        return

    categories = get_all_categories()

    await update.callback_query.edit_message_text(
        text=build_faq_categories_text(lang),
        reply_markup=faq_categories_keyboard(lang, categories),
    )


async def handle_faq_action(
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
    parts = raw_data.split(":")

    if len(parts) < 2:
        await query.edit_message_text(text=t(lang, "FAQ_NOT_FOUND"))
        return

    action = parts[1]

    if action == "categories":
        categories = get_all_categories()
        await query.edit_message_text(
            text=build_faq_categories_text(lang),
            reply_markup=faq_categories_keyboard(lang, categories),
        )
        return

    if action == "category" and len(parts) == 3:
        category_id = parts[2]
        category = get_category_by_id(category_id)

        if category is None:
            await query.edit_message_text(text=t(lang, "FAQ_NOT_FOUND"))
            return

        if not category.items:
            await query.edit_message_text(text=t(lang, "FAQ_EMPTY_CATEGORY"))
            return

        category_title = category.title.model_dump()[lang]

        await query.edit_message_text(
            text=build_faq_questions_text(lang, category_title),
            reply_markup=faq_questions_keyboard(lang, category),
        )
        return

    if action == "item" and len(parts) == 4:
        category_id = parts[2]
        item_id = parts[3]

        item = get_item_by_id(category_id, item_id)

        if item is None:
            await query.edit_message_text(text=t(lang, "FAQ_NOT_FOUND"))
            return

        question = item.q.model_dump()[lang]
        answer = item.a.model_dump()[lang]

        await query.edit_message_text(
            text=build_faq_answer_text(lang, question, answer),
            reply_markup=faq_answer_keyboard(lang, category_id),
        )
        return

    await query.edit_message_text(text=t(lang, "FAQ_NOT_FOUND"))