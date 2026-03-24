from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.schemas.faq import FAQCategory, FAQDataset, FAQItem


FAQ_FILE_PATH = Path("app/seed/faqs.json")


@lru_cache(maxsize=1)
def load_faq_dataset() -> FAQDataset:
    with FAQ_FILE_PATH.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    return FAQDataset.model_validate(raw_data)


def get_all_categories() -> list[FAQCategory]:
    return load_faq_dataset().categories


def get_category_by_id(category_id: str) -> FAQCategory | None:
    for category in load_faq_dataset().categories:
        if category.id == category_id:
            return category
    return None


def get_item_by_id(category_id: str, item_id: str) -> FAQItem | None:
    category = get_category_by_id(category_id)
    if category is None:
        return None

    for item in category.items:
        if item.id == item_id:
            return item
    return None