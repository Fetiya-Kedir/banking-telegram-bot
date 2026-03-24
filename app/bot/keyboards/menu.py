from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.i18n.translator import t
from app.bot.keyboards.common import navigation_rows
from app.config.constants import (
    MENU_ABOUT,
    MENU_ATM,
    MENU_BRANCH,
    MENU_CALLBACK_PREFIX,
    MENU_CONTACT,
    MENU_FAQ,
    MENU_SUPPORT,
)


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                t(lang, "MENU_BRANCH"),
                callback_data=f"{MENU_CALLBACK_PREFIX}{MENU_BRANCH}",
            ),
            InlineKeyboardButton(
                t(lang, "MENU_ATM"),
                callback_data=f"{MENU_CALLBACK_PREFIX}{MENU_ATM}",
            ),
        ],
        [
            InlineKeyboardButton(
                t(lang, "MENU_FAQ"),
                callback_data=f"{MENU_CALLBACK_PREFIX}{MENU_FAQ}",
            ),
            InlineKeyboardButton(
                t(lang, "MENU_SUPPORT"),
                callback_data=f"{MENU_CALLBACK_PREFIX}{MENU_SUPPORT}",
            ),
        ],
        [
            InlineKeyboardButton(
                t(lang, "MENU_ABOUT"),
                callback_data=f"{MENU_CALLBACK_PREFIX}{MENU_ABOUT}",
            ),
            InlineKeyboardButton(
                t(lang, "MENU_CONTACT"),
                callback_data=f"{MENU_CALLBACK_PREFIX}{MENU_CONTACT}",
            ),
        ],
    ]

    rows.extend(
        navigation_rows(
            lang,
            include_back=False,
            include_home=False,
            include_change_language=True,
        )
    )

    return InlineKeyboardMarkup(rows)