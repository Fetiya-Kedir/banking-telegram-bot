from __future__ import annotations

from pydantic import BaseModel


class LocalizedText(BaseModel):
    en: str
    am: str
    om: str


class FAQItem(BaseModel):
    id: str
    q: LocalizedText
    a: LocalizedText


class FAQCategory(BaseModel):
    id: str
    title: LocalizedText
    items: list[FAQItem]


class FAQDataset(BaseModel):
    categories: list[FAQCategory]