from __future__ import annotations

import asyncio

from telegram import LinkPreviewOptions, ReplyKeyboardRemove, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from app.bot.i18n.translator import t
from app.bot.keyboards.atm import (
    atm_menu_keyboard,
    atm_prompt_keyboard,
    atm_results_keyboard,
    request_atm_location_keyboard,
)
from app.services.atm_service import get_nearest_atms, search_atms
from app.services.user_service import get_user_language


ATM_MODE_KEY = "atm_mode"
ACTIVE_ATM_MENU_MESSAGE_ID_KEY = "active_atm_menu_message_id"
ATM_LOCATION_REQUEST_MESSAGE_ID_KEY = "atm_location_request_message_id"

ATM_MODE_TEXT = "awaiting_atm_text"
ATM_MODE_LOCATION = "awaiting_atm_location"

RESULT_SEPARATOR = "\n────────────────────────\n"


def clear_atm_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(ATM_MODE_KEY, None)
    context.user_data.pop(ATM_LOCATION_REQUEST_MESSAGE_ID_KEY, None)


def set_active_atm_menu_message_id(
    context: ContextTypes.DEFAULT_TYPE,
    message_id: int,
) -> None:
    context.user_data[ACTIVE_ATM_MENU_MESSAGE_ID_KEY] = message_id


def get_active_atm_menu_message_id(context: ContextTypes.DEFAULT_TYPE) -> int | None:
    return context.user_data.get(ACTIVE_ATM_MENU_MESSAGE_ID_KEY)


def set_atm_location_request_message_id(
    context: ContextTypes.DEFAULT_TYPE,
    message_id: int,
) -> None:
    context.user_data[ATM_LOCATION_REQUEST_MESSAGE_ID_KEY] = message_id


def get_atm_location_request_message_id(
    context: ContextTypes.DEFAULT_TYPE,
) -> int | None:
    return context.user_data.get(ATM_LOCATION_REQUEST_MESSAGE_ID_KEY)


def build_atm_menu_text(lang: str) -> str:
    return (
        f"{t(lang, 'ATM_MENU_TITLE')}\n\n"
        f"{t(lang, 'ATM_MENU_PROMPT')}"
    )


def build_atm_text_prompt(lang: str) -> str:
    return (
        f"{t(lang, 'ATM_MENU_TITLE')}\n\n"
        f"{t(lang, 'ATM_TEXT_PROMPT')}\n"
        f"{t(lang, 'ATM_TEXT_HINT')}"
    )


def build_atm_location_prompt(lang: str) -> str:
    return (
        f"{t(lang, 'ATM_MENU_TITLE')}\n\n"
        f"{t(lang, 'ATM_LOCATION_PROMPT')}\n"
        f"{t(lang, 'ATM_LOCATION_HINT')}"
    )


def get_localized_value(localized_obj, lang: str) -> str:
    data = localized_obj.model_dump()
    return data.get(lang) or data.get("en") or ""


def build_map_url(latitude: float, longitude: float) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"


def atm_services_text(lang: str) -> str:
    return (
        f"{t(lang, 'ATM_SERVICES_TITLE')}: "
        f"{t(lang, 'ATM_SERVICE_WITHDRAWAL')}, "
        f"{t(lang, 'ATM_SERVICE_BALANCE')}"
    )


def format_atm_entry(atm, lang: str, distance_km: float | None = None) -> str:
    name = get_localized_value(atm.name, lang)
    location = get_localized_value(atm.location, lang)
    desc = get_localized_value(atm.desc, lang)
    map_url = build_map_url(atm.latitude, atm.longitude)

    lines = [
        f"🏧 {name}",
        f"📍 {location}",
        f"🗺️ {desc}",
        f"🗺️ Map: {map_url}",
        f"💳 {atm_services_text(lang)}",
    ]

    if distance_km is not None:
        lines.append(f"📏 {distance_km:.2f} km")

    return "\n".join(lines)


def build_atm_search_results_text(lang: str, atms: list) -> str:
    if not atms:
        return t(lang, "ATM_NO_RESULTS")

    entries = [format_atm_entry(atm, lang) for atm in atms]
    return RESULT_SEPARATOR.join(entries)


def build_atm_nearby_results_text(lang: str, atms_with_distance: list[tuple]) -> str:
    if not atms_with_distance:
        return t(lang, "ATM_NO_RESULTS")

    entries = [
        format_atm_entry(atm, lang, distance)
        for atm, distance in atms_with_distance
    ]
    return RESULT_SEPARATOR.join(entries)


async def show_atm_menu_screen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    lang: str,
) -> None:
    if update.callback_query is None:
        return

    clear_atm_state(context)
    set_active_atm_menu_message_id(context, update.callback_query.message.message_id)

    await update.callback_query.edit_message_text(
        text=build_atm_menu_text(lang),
        reply_markup=atm_menu_keyboard(lang),
    )


async def handle_atm_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.callback_query is None or update.effective_user is None:
        return

    query = update.callback_query
    await query.answer()

    settings = context.application.bot_data["settings"]
    session_factory = context.application.bot_data["session_factory"]

    async with session_factory() as session:
        lang = await get_user_language(
            session=session,
            telegram_user_id=update.effective_user.id,
            default_language=settings.default_language,
        )

    raw_data = query.data or ""
    _, action = raw_data.split(":", maxsplit=1)

    set_active_atm_menu_message_id(context, query.message.message_id)

    if action == "menu":
        clear_atm_state(context)
        await query.edit_message_text(
            text=build_atm_menu_text(lang),
            reply_markup=atm_menu_keyboard(lang),
        )
        return

    if action == "text":
        context.user_data[ATM_MODE_KEY] = ATM_MODE_TEXT
        await query.edit_message_text(
            text=build_atm_text_prompt(lang),
            reply_markup=atm_prompt_keyboard(lang),
        )
        return

    if action == "location":
        context.user_data[ATM_MODE_KEY] = ATM_MODE_LOCATION
        await query.edit_message_text(
            text=build_atm_location_prompt(lang),
            reply_markup=atm_prompt_keyboard(lang),
        )

        request_message = await query.message.reply_text(
            text=t(lang, "ATM_LOCATION_PROMPT"),
            reply_markup=request_atm_location_keyboard(lang),
        )
        set_atm_location_request_message_id(context, request_message.message_id)
        return


async def handle_atm_text_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.effective_user is None:
        return

    if context.user_data.get(ATM_MODE_KEY) != ATM_MODE_TEXT:
        return

    query_text = update.message.text.strip()
    if not query_text:
        return

    settings = context.application.bot_data["settings"]
    session_factory = context.application.bot_data["session_factory"]

    async with session_factory() as session:
        lang = await get_user_language(
            session=session,
            telegram_user_id=update.effective_user.id,
            default_language=settings.default_language,
        )

    results = search_atms(
        query=query_text,
        limit=settings.max_nearest_results,
    )

    old_message_id = get_active_atm_menu_message_id(context)

    result_text = build_atm_search_results_text(lang, results)

    result_message = await update.message.reply_text(
        text=result_text,
        reply_markup=atm_results_keyboard(lang),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )

    set_active_atm_menu_message_id(context, result_message.message_id)
    clear_atm_state(context)

    if old_message_id is not None and update.effective_chat is not None:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=old_message_id,
            )
        except BadRequest:
            pass


async def handle_atm_location_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.message.location is None or update.effective_user is None:
        return

    if context.user_data.get(ATM_MODE_KEY) != ATM_MODE_LOCATION:
        return

    settings = context.application.bot_data["settings"]
    session_factory = context.application.bot_data["session_factory"]

    async with session_factory() as session:
        lang = await get_user_language(
            session=session,
            telegram_user_id=update.effective_user.id,
            default_language=settings.default_language,
        )

    results = get_nearest_atms(
        latitude=update.message.location.latitude,
        longitude=update.message.location.longitude,
        limit=settings.max_nearest_results,
    )

    old_message_id = get_active_atm_menu_message_id(context)
    request_message_id = get_atm_location_request_message_id(context)

    try:
        await update.message.delete()
    except BadRequest:
        pass

    if request_message_id is not None and update.effective_chat is not None:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=request_message_id,
            )
        except BadRequest:
            pass

    cleanup_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="…",
        reply_markup=ReplyKeyboardRemove(),
    )

    result_text = build_atm_nearby_results_text(lang, results)

    result_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=result_text,
        reply_markup=atm_results_keyboard(lang),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )

    set_active_atm_menu_message_id(context, result_message.message_id)
    clear_atm_state(context)

    if old_message_id is not None and update.effective_chat is not None:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=old_message_id,
            )
        except BadRequest:
            pass

    await asyncio.sleep(0.4)
    try:
        await cleanup_message.delete()
    except BadRequest:
        pass