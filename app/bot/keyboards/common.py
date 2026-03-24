from telegram import InlineKeyboardButton

from app.bot.i18n.translator import t
from app.config.constants import NAV_BACK, NAV_CALLBACK_PREFIX, NAV_CHANGE_LANGUAGE, NAV_HOME


def navigation_rows(
    lang: str,
    *,
    include_back: bool = False,
    include_home: bool = False,
    include_change_language: bool = True,
) -> list[list[InlineKeyboardButton]]:
    rows: list[list[InlineKeyboardButton]] = []

    first_row: list[InlineKeyboardButton] = []

    if include_back:
        first_row.append(
            InlineKeyboardButton(
                t(lang, "BACK"),
                callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_BACK}",
            )
        )

    if include_home:
        first_row.append(
            InlineKeyboardButton(
                t(lang, "BACK_TO_MAIN_MENU"),
                callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_HOME}",
            )
        )

    if first_row:
        rows.append(first_row)

    if include_change_language:
        rows.append(
            [
                InlineKeyboardButton(
                    t(lang, "CHANGE_LANGUAGE"),
                    callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_CHANGE_LANGUAGE}",
                )
            ]
        )

    return rows