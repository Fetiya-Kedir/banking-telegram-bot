from __future__ import annotations

import logging

from app.bot.application import build_application
from app.config.logging import setup_logging
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()

    setup_logging(settings.log_level)

    application = build_application(settings.bot_token)

    logger.info("%s is starting...", settings.app_name)

    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()