from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.bot.handlers.atm import (
    ATM_MODE_KEY,
    ATM_MODE_LOCATION,
    ATM_MODE_TEXT,
    handle_atm_action,
    handle_atm_location_input,
    handle_atm_text_input,
)
from app.bot.handlers.branch import (
    BRANCH_MODE_KEY,
    BRANCH_MODE_LOCATION,
    BRANCH_MODE_TEXT,
    handle_branch_action,
    handle_branch_location_input,
    handle_branch_text_input,
)
from app.bot.handlers.faq import handle_faq_action
from app.bot.handlers.language import handle_language_selection
from app.bot.handlers.menu import handle_menu_action
from app.bot.handlers.navigation import handle_navigation_action
from app.bot.handlers.start import start_command
from app.config.constants import (
    ATM_CALLBACK_PREFIX,
    BRANCH_CALLBACK_PREFIX,
    FAQ_CALLBACK_PREFIX,
    LANGUAGE_CALLBACK_PREFIX,
    MENU_CALLBACK_PREFIX,
    NAV_CALLBACK_PREFIX,
)
from app.config.settings import get_settings
from app.db.session import AsyncSessionLocal, close_db, init_db

logger = logging.getLogger(__name__)


async def on_startup(application: Application) -> None:
    await init_db()
    logger.info("Database initialized successfully.")


async def on_shutdown(application: Application) -> None:
    await close_db()
    logger.info("Database connections closed.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled exception while processing update.", exc_info=context.error)


async def route_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mode = context.user_data.get(BRANCH_MODE_KEY)
    if mode == BRANCH_MODE_TEXT:
        await handle_branch_text_input(update, context)
        return

    mode = context.user_data.get(ATM_MODE_KEY)
    if mode == ATM_MODE_TEXT:
        await handle_atm_text_input(update, context)
        return


async def route_location_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mode = context.user_data.get(BRANCH_MODE_KEY)
    if mode == BRANCH_MODE_LOCATION:
        await handle_branch_location_input(update, context)
        return

    mode = context.user_data.get(ATM_MODE_KEY)
    if mode == ATM_MODE_LOCATION:
        await handle_atm_location_input(update, context)
        return


def build_application(bot_token: str) -> Application:
    settings = get_settings()

    application = (
        ApplicationBuilder()
        .token(bot_token)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    application.bot_data["settings"] = settings
    application.bot_data["session_factory"] = AsyncSessionLocal

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(
        CallbackQueryHandler(
            handle_language_selection,
            pattern=rf"^{LANGUAGE_CALLBACK_PREFIX}",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            handle_faq_action,
            pattern=rf"^{FAQ_CALLBACK_PREFIX}",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            handle_branch_action,
            pattern=rf"^{BRANCH_CALLBACK_PREFIX}",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            handle_atm_action,
            pattern=rf"^{ATM_CALLBACK_PREFIX}",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            handle_navigation_action,
            pattern=rf"^{NAV_CALLBACK_PREFIX}",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            handle_menu_action,
            pattern=rf"^{MENU_CALLBACK_PREFIX}",
        )
    )

    application.add_handler(MessageHandler(filters.LOCATION, route_location_input))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, route_text_input)
    )

    application.add_error_handler(error_handler)

    return application