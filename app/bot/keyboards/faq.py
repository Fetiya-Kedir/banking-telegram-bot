from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.i18n.translator import t
from app.bot.keyboards.common import navigation_rows
from app.config.constants import FAQ_CALLBACK_PREFIX, NAV_CALLBACK_PREFIX, NAV_HOME
from app.schemas.faq import FAQCategory


def chunk_buttons(buttons: list[InlineKeyboardButton], size: int = 2) -> list[list[InlineKeyboardButton]]:
    return [buttons[i:i + size] for i in range(0, len(buttons), size)]


def faq_categories_keyboard(lang: str, categories: list[FAQCategory]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            category.title.model_dump()[lang],
            callback_data=f"{FAQ_CALLBACK_PREFIX}category:{category.id}",
        )
        for category in categories
    ]

    rows = chunk_buttons(buttons, size=2)

    rows.extend(
        navigation_rows(
            lang,
            include_back=False,
            include_home=True,
            include_change_language=True,
        )
    )

    return InlineKeyboardMarkup(rows)


def faq_questions_keyboard(lang: str, category: FAQCategory) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []

    for item in category.items:
        rows.append(
            [
                InlineKeyboardButton(
                    item.q.model_dump()[lang],
                    callback_data=f"{FAQ_CALLBACK_PREFIX}item:{category.id}:{item.id}",
                )
            ]
        )

    rows.append(
        [
            InlineKeyboardButton(
                t(lang, "FAQ_BACK_TO_CATEGORIES"),
                callback_data=f"{FAQ_CALLBACK_PREFIX}categories",
            ),
            InlineKeyboardButton(
                t(lang, "BACK_TO_MAIN_MENU"),
                callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_HOME}",
            ),
        ]
    )

    rows.extend(
        navigation_rows(
            lang,
            include_back=False,
            include_home=False,
            include_change_language=True,
        )
    )

    return InlineKeyboardMarkup(rows)


def faq_answer_keyboard(lang: str, category_id: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                t(lang, "BACK"),
                callback_data=f"{FAQ_CALLBACK_PREFIX}category:{category_id}",
            ),
            InlineKeyboardButton(
                t(lang, "FAQ_BACK_TO_CATEGORIES"),
                callback_data=f"{FAQ_CALLBACK_PREFIX}categories",
            ),
        ],
        [
            InlineKeyboardButton(
                t(lang, "BACK_TO_MAIN_MENU"),
                callback_data=f"{NAV_CALLBACK_PREFIX}{NAV_HOME}",
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