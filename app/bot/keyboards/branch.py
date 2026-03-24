from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.bot.i18n.translator import t
from app.config.constants import BRANCH_CALLBACK_PREFIX, NAV_CALLBACK_PREFIX, NAV_CHANGE_LANGUAGE, NAV_HOME


def branch_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t(lang, "BRANCH_SEARCH_BY_TEXT"),
                    callback_data=f"{BRANCH_CALLBACK_PREFIX}text",
                ),
                InlineKeyboardButton(
                    t(lang, "BRANCH_SHARE_LOCATION"),
                    callback_data=f"{BRANCH_CALLBACK_PREFIX}location",
                ),
            ],
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


def branch_prompt_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t(lang, "BACK_TO_BRANCH_MENU"),
                    callback_data=f"{BRANCH_CALLBACK_PREFIX}menu",
                ),
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


def branch_results_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t(lang, "BACK_TO_BRANCH_MENU"),
                    callback_data=f"{BRANCH_CALLBACK_PREFIX}menu",
                ),
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


def request_location_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=t(lang, "BRANCH_SEND_LOCATION_BUTTON"),
                    request_location=True,
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )