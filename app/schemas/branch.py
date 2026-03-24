from __future__ import annotations

from pydantic import BaseModel


class LocalizedText(BaseModel):
    en: str
    am: str
    om: str


class Branch(BaseModel):
    id: str
    name: LocalizedText
    city: LocalizedText
    region: LocalizedText
    address: LocalizedText
    plus_code: str = ""
    latitude: float
    longitude: float


class BranchDataset(BaseModel):
    branches: list[Branch]