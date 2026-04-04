from __future__ import annotations

from telegram import Update
from telegram.error import BadRequest, ChatMigrated
from telegram.ext import ContextTypes

from app.bot.i18n.translator import t
from app.bot.keyboards.language import language_keyboard
from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.keyboards.support import support_confirmation_keyboard, support_prompt_keyboard
from app.services.support_service import create_support_ticket_and_forward
from app.services.user_service import get_user_language, upsert_telegram_user


SUPPORT_MODE_KEY = "support_mode"
ACTIVE_SUPPORT_MESSAGE_ID_KEY = "active_support_message_id"

SUPPORT_MODE_AWAITING_QUESTION = "awaiting_support_question"


def clear_support_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(SUPPORT_MODE_KEY, None)


def set_active_support_message_id(
    context: ContextTypes.DEFAULT_TYPE,
    message_id: int,
) -> None:
    context.user_data[ACTIVE_SUPPORT_MESSAGE_ID_KEY] = message_id


def get_active_support_message_id(context: ContextTypes.DEFAULT_TYPE) -> int | None:
    return context.user_data.get(ACTIVE_SUPPORT_MESSAGE_ID_KEY)


def build_support_prompt_text(lang: str) -> str:
    return (
        f"{t(lang, 'SUPPORT_PROMPT_TITLE')}\n\n"
        f"{t(lang, 'SUPPORT_PROMPT_BODY')}\n"
        f"{t(lang, 'SUPPORT_PROMPT_HINT')}"
    )


def build_support_confirmation_text(lang: str, ticket_code: str) -> str:
    return (
        f"{t(lang, 'SUPPORT_SENT_TITLE')}\n"
        f"{t(lang, 'SUPPORT_REFERENCE').format(ticket_code=ticket_code)}\n\n"
        f"{t(lang, 'SUPPORT_WAIT_RESPONSE')}"
    )


def build_followup_main_menu_text(lang: str, display_name: str) -> str:
    return (
        f"{t(lang, 'WELCOME_MAIN_MENU').format(name=display_name)}\n\n"
        f"{t(lang, 'MAIN_MENU_PROMPT')}"
    )


async def retire_support_message_keyboard(update: Update) -> None:
    if update.callback_query is None:
        return

    try:
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
    except BadRequest:
        pass


async def show_support_prompt_screen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    lang: str,
) -> None:
    if update.callback_query is None:
        return

    clear_support_state(context)
    context.user_data[SUPPORT_MODE_KEY] = SUPPORT_MODE_AWAITING_QUESTION
    set_active_support_message_id(context, update.callback_query.message.message_id)

    await update.callback_query.edit_message_text(
        text=build_support_prompt_text(lang),
        reply_markup=support_prompt_keyboard(lang),
    )


async def handle_support_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.callback_query is None or update.effective_user is None or update.effective_chat is None:
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

    if action == "ask_again":
        clear_support_state(context)
        context.user_data[SUPPORT_MODE_KEY] = SUPPORT_MODE_AWAITING_QUESTION

        await retire_support_message_keyboard(update)

        prompt_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=build_support_prompt_text(lang),
            reply_markup=support_prompt_keyboard(lang),
        )
        set_active_support_message_id(context, prompt_message.message_id)
        return

    if action == "home":
        clear_support_state(context)
        await retire_support_message_keyboard(update)

        display_name = update.effective_user.first_name or "there"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=build_followup_main_menu_text(lang, display_name),
            reply_markup=main_menu_keyboard(lang),
        )
        return

    if action == "change_language":
        clear_support_state(context)
        await retire_support_message_keyboard(update)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t(lang, "LANGUAGE_PROMPT"),
            reply_markup=language_keyboard(),
        )
        return


async def handle_support_question_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.effective_user is None:
        return

    if context.user_data.get(SUPPORT_MODE_KEY) != SUPPORT_MODE_AWAITING_QUESTION:
        return

    question_text = update.message.text.strip()
    if not question_text:
        return

    settings = context.application.bot_data["settings"]
    session_factory = context.application.bot_data["session_factory"]

    async with session_factory() as session:
        db_user = await upsert_telegram_user(
            session=session,
            telegram_user=update.effective_user,
            default_language=settings.default_language,
        )

        lang = db_user.language_code_selected

        try:
            ticket = await create_support_ticket_and_forward(
                session=session,
                bot=context.bot,
                admin_group_id=settings.admin_group_id,
                db_user=db_user,
                telegram_user=update.effective_user,
                question_text=question_text,
                language_code_selected=lang,
            )
        except ChatMigrated as e:
            clear_support_state(context)
            await update.message.reply_text(
                text=(
                    f"{t(lang, 'SUPPORT_TEMP_UNAVAILABLE')}\n\n"
                    f"Admin group migrated. Update ADMIN_GROUP_ID to: {e.new_chat_id}"
                ),
                reply_markup=support_prompt_keyboard(lang),
            )
            return
        except BadRequest:
            clear_support_state(context)
            await update.message.reply_text(
                text=t(lang, "SUPPORT_TEMP_UNAVAILABLE"),
                reply_markup=support_prompt_keyboard(lang),
            )
            return

    confirmation_message = await update.message.reply_text(
        text=build_support_confirmation_text(lang, ticket.ticket_code),
        reply_markup=support_confirmation_keyboard(lang),
    )

    set_active_support_message_id(context, confirmation_message.message_id)
    clear_support_state(context)