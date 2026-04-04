from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.i18n.translator import t
from app.config.constants import NAV_CALLBACK_PREFIX, NAV_CHANGE_LANGUAGE, NAV_HOME, SUPPORT_CALLBACK_PREFIX


def support_prompt_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t(lang, "BACK_TO_MAIN_MENU"),
                    callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_HOME}",
                ),
            ],
            [
                InlineKeyboardButton(
                    t(lang, "CHANGE_LANGUAGE"),
                    callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_CHANGE_LANGUAGE}",
                ),
            ],
        ]
    )


def support_confirmation_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t(lang, "SUPPORT_ASK_ANOTHER"),
                    callback_data=f"{SUPPORT_CALLBACK_PREFIX}ask_again",
                ),
            ],
            [
                InlineKeyboardButton(
                    t(lang, "BACK_TO_MAIN_MENU"),
                    callback_data=f"{SUPPORT_CALLBACK_PREFIX}home",
                ),
            ],
            [
                InlineKeyboardButton(
                    t(lang, "CHANGE_LANGUAGE"),
                    callback_data=f"{SUPPORT_CALLBACK_PREFIX}change_language",
                ),
            ],
        ]
    )