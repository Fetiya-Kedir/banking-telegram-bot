from __future__ import annotations

import asyncio

from telegram import LinkPreviewOptions, ReplyKeyboardRemove, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from app.bot.i18n.translator import t
from app.bot.keyboards.branch import (
    branch_menu_keyboard,
    branch_prompt_keyboard,
    branch_results_keyboard,
    request_location_keyboard,
)
from app.services.branch_service import get_nearest_branches, search_branches
from app.services.user_service import get_user_language


BRANCH_MODE_KEY = "branch_mode"
ACTIVE_MENU_MESSAGE_ID_KEY = "active_menu_message_id"
LOCATION_REQUEST_MESSAGE_ID_KEY = "location_request_message_id"

BRANCH_MODE_TEXT = "awaiting_branch_text"
BRANCH_MODE_LOCATION = "awaiting_branch_location"

RESULT_SEPARATOR = "\n────────────────────────\n"


def clear_location_request_message_id(
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    context.user_data.pop(LOCATION_REQUEST_MESSAGE_ID_KEY, None)


def clear_branch_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(BRANCH_MODE_KEY, None)
    clear_location_request_message_id(context)


def set_location_request_message_id(
    context: ContextTypes.DEFAULT_TYPE,
    message_id: int,
) -> None:
    context.user_data[LOCATION_REQUEST_MESSAGE_ID_KEY] = message_id


def get_location_request_message_id(
    context: ContextTypes.DEFAULT_TYPE,
) -> int | None:
    return context.user_data.get(LOCATION_REQUEST_MESSAGE_ID_KEY)


def set_active_menu_message_id(
    context: ContextTypes.DEFAULT_TYPE,
    message_id: int,
) -> None:
    context.user_data[ACTIVE_MENU_MESSAGE_ID_KEY] = message_id


def get_active_menu_message_id(context: ContextTypes.DEFAULT_TYPE) -> int | None:
    return context.user_data.get(ACTIVE_MENU_MESSAGE_ID_KEY)


def build_branch_menu_text(lang: str) -> str:
    return (
        f"{t(lang, 'BRANCH_MENU_TITLE')}\n\n"
        f"{t(lang, 'BRANCH_MENU_PROMPT')}"
    )


def build_branch_text_prompt(lang: str) -> str:
    return (
        f"{t(lang, 'BRANCH_MENU_TITLE')}\n\n"
        f"{t(lang, 'BRANCH_TEXT_PROMPT')}\n\n"
        f"{t(lang, 'BRANCH_TEXT_HINT')}"
    )


def build_branch_location_prompt(lang: str) -> str:
    return (
        f"{t(lang, 'BRANCH_MENU_TITLE')}\n\n"
        f"{t(lang, 'BRANCH_LOCATION_PROMPT')}\n\n"
        f"{t(lang, 'BRANCH_LOCATION_HINT')}"
    )


def get_localized_value(localized_obj, lang: str) -> str:
    data = localized_obj.model_dump()
    return data.get(lang) or data.get("en") or ""


def build_map_url(latitude: float, longitude: float) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"


def build_area_label(city: str, address: str) -> str:
    address_head = address.split(",")[0].strip() if address else ""

    if city and address_head:
        if city.lower() == address_head.lower():
            return city
        return f"{city} - {address_head}"

    return city or address_head or ""


def format_branch_entry(branch, lang: str, distance_km: float | None = None) -> str:
    name = get_localized_value(branch.name, lang)
    city = get_localized_value(branch.city, lang)
    address = get_localized_value(branch.address, lang)

    map_url = build_map_url(branch.latitude, branch.longitude)
    area_label = build_area_label(city, address)

    lines = [
        f"🏦 {name}",
        f"📍 {address}",
    ]

    if area_label:
        lines.append(f"🗺️ {area_label}")

    lines.append(f"🗺️ Map: {map_url}")

    if distance_km is not None:
        lines.append(f"📏 {distance_km:.2f} km")

    return "\n".join(lines)


def build_branch_search_results_text(lang: str, branches: list) -> str:
    if not branches:
        return t(lang, "BRANCH_NO_RESULTS")

    intro = t(lang, "BRANCH_SEARCH_RESULTS_TITLE")
    entries = [format_branch_entry(branch, lang) for branch in branches]

    return f"{intro}\n\n{RESULT_SEPARATOR.join(entries)}"


def build_branch_nearby_results_text(lang: str, branches_with_distance: list[tuple]) -> str:
    if not branches_with_distance:
        return t(lang, "BRANCH_NO_RESULTS")

    intro = t(lang, "BRANCH_NEARBY_RESULTS_TITLE")
    entries = [
        format_branch_entry(branch, lang, distance)
        for branch, distance in branches_with_distance
    ]

    return f"{intro}\n\n{RESULT_SEPARATOR.join(entries)}"


async def show_branch_menu_screen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    lang: str,
) -> None:
    if update.callback_query is None:
        return

    clear_branch_state(context)
    set_active_menu_message_id(context, update.callback_query.message.message_id)

    await update.callback_query.edit_message_text(
        text=build_branch_menu_text(lang),
        reply_markup=branch_menu_keyboard(lang),
    )


async def handle_branch_action(
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

    set_active_menu_message_id(context, query.message.message_id)

    if action == "menu":
        clear_branch_state(context)
        await query.edit_message_text(
            text=build_branch_menu_text(lang),
            reply_markup=branch_menu_keyboard(lang),
        )
        return

    if action == "text":
        context.user_data[BRANCH_MODE_KEY] = BRANCH_MODE_TEXT
        await query.edit_message_text(
            text=build_branch_text_prompt(lang),
            reply_markup=branch_prompt_keyboard(lang),
        )
        return

    if action == "location":
        context.user_data[BRANCH_MODE_KEY] = BRANCH_MODE_LOCATION
        await query.edit_message_text(
            text=build_branch_location_prompt(lang),
            reply_markup=branch_prompt_keyboard(lang),
        )

        request_message = await query.message.reply_text(
            text=t(lang, "BRANCH_LOCATION_PROMPT"),
            reply_markup=request_location_keyboard(lang),
        )
        set_location_request_message_id(context, request_message.message_id)
        return


async def handle_branch_text_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.effective_user is None:
        return

    if context.user_data.get(BRANCH_MODE_KEY) != BRANCH_MODE_TEXT:
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

    results = search_branches(
        query=query_text,
        limit=settings.max_nearest_results,
    )

    old_message_id = get_active_menu_message_id(context)

    result_text = build_branch_search_results_text(lang, results)

    result_message = await update.message.reply_text(
        text=result_text,
        reply_markup=branch_results_keyboard(lang),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )

    set_active_menu_message_id(context, result_message.message_id)
    clear_branch_state(context)

    if old_message_id is not None and update.effective_chat is not None:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=old_message_id,
            )
        except BadRequest:
            pass


async def handle_branch_location_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None or update.message.location is None or update.effective_user is None:
        return

    if context.user_data.get(BRANCH_MODE_KEY) != BRANCH_MODE_LOCATION:
        return

    settings = context.application.bot_data["settings"]
    session_factory = context.application.bot_data["session_factory"]

    async with session_factory() as session:
        lang = await get_user_language(
            session=session,
            telegram_user_id=update.effective_user.id,
            default_language=settings.default_language,
        )

    results = get_nearest_branches(
        latitude=update.message.location.latitude,
        longitude=update.message.location.longitude,
        limit=settings.max_nearest_results,
    )

    old_message_id = get_active_menu_message_id(context)
    request_message_id = get_location_request_message_id(context)

    # Keep the user's location message visible for better conversation context.

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

    result_text = build_branch_nearby_results_text(lang, results)

    result_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=result_text,
        reply_markup=branch_results_keyboard(lang),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )

    set_active_menu_message_id(context, result_message.message_id)
    clear_branch_state(context)

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