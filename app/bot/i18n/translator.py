from __future__ import annotations

from app.bot.i18n.locales import MESSAGES


def t(lang: str, key: str) -> str:
    lang = (lang or "en").strip().lower()

    lang_map = MESSAGES.get(key)
    if lang_map is None:
        return key

    return lang_map.get(lang) or lang_map.get("en") or key