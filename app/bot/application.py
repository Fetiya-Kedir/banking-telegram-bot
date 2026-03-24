from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

from app.bot.handlers.start import start_command
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


def build_application(bot_token: str) -> Application:
    application = (
        ApplicationBuilder()
        .token(bot_token)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    application.bot_data["session_factory"] = AsyncSessionLocal

    application.add_handler(CommandHandler("start", start_command))
    application.add_error_handler(error_handler)

    return application