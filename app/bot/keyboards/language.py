from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.config.constants import LANGUAGE_CALLBACK_PREFIX


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("English", callback_data=f"{LANGUAGE_CALLBACK_PREFIX}en"),
                InlineKeyboardButton("አማርኛ", callback_data=f"{LANGUAGE_CALLBACK_PREFIX}am"),
            ],
            [
                InlineKeyboardButton("Afaan Oromo", callback_data=f"{LANGUAGE_CALLBACK_PREFIX}om"),
            ],
        ]
    )