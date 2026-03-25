from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.i18n.translator import t
from app.config.constants import NAV_CALLBACK_PREFIX, NAV_CHANGE_LANGUAGE, NAV_HOME


def about_keyboard(lang: str, website_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t(lang, "CONTACT_WEBSITE_LABEL"),
                    url=website_url,
                )
            ],
            [
                InlineKeyboardButton(
                    t(lang, "BACK_TO_MAIN_MENU"),
                    callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_HOME}",
                )
            ],
            [
                InlineKeyboardButton(
                    t(lang, "CHANGE_LANGUAGE"),
                    callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_CHANGE_LANGUAGE}",
                )
            ],
        ]
    )


def contact_keyboard(
    lang: str,
    *,
    website_url: str,
    telegram_url: str | None = None,
    facebook_url: str | None = None,
    instagram_url: str | None = None,
    tiktok_url: str | None = None,
    youtube_url: str | None = None,
    linkedin_url: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                t(lang, "CONTACT_WEBSITE_LABEL"),
                url=website_url,
            )
        ]
    ]

    if telegram_url:
        rows.append(
            [
                InlineKeyboardButton(
                    t(lang, "CONTACT_TELEGRAM_LABEL"),
                    url=telegram_url,
                )
            ]
        )

    if facebook_url:
        rows.append(
            [
                InlineKeyboardButton(
                    t(lang, "CONTACT_FACEBOOK_LABEL"),
                    url=facebook_url,
                )
            ]
        )

    if instagram_url:
        rows.append(
            [
                InlineKeyboardButton(
                    t(lang, "CONTACT_INSTAGRAM_LABEL"),
                    url=instagram_url,
                )
            ]
        )


    if tiktok_url:
        rows.append(
            [
                InlineKeyboardButton(
                    t(lang, "CONTACT_TIKTOK_LABEL"),
                    url=tiktok_url,
                )
            ]
        )

    if youtube_url:
        rows.append(
            [
                InlineKeyboardButton(
                    t(lang, "CONTACT_YOUTUBE_LABEL"),
                    url=youtube_url,
                )
            ]
        )

    if linkedin_url:
        rows.append(
            [
                InlineKeyboardButton(
                    t(lang, "CONTACT_LINKEDIN_LABEL"),
                    url=linkedin_url,
                )
            ]
        )

    rows.append(
        [
            InlineKeyboardButton(
                t(lang, "BACK_TO_MAIN_MENU"),
                callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_HOME}",
            )
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(
                t(lang, "CHANGE_LANGUAGE"),
                callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_CHANGE_LANGUAGE}",
            )
        ]
    )

    return InlineKeyboardMarkup(rows)