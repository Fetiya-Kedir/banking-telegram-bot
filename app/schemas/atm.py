from __future__ import annotations

from pydantic import BaseModel


class LocalizedText(BaseModel):
    en: str
    am: str
    om: str


class ATMServices(BaseModel):
    cash_withdrawal: bool = True
    balance_inquiry: bool = True
    cash_deposit: bool = False
    mini_statement: bool = False
    fund_transfer: bool = False


class ATM(BaseModel):
    id: str
    sno: int
    name: LocalizedText
    location: LocalizedText
    desc: LocalizedText
    latitude: float
    longitude: float
    services: ATMServices
    smart_capable: bool = False
    smart_features_enabled: bool = False
    is_active: bool = True


class ATMDataset(BaseModel):
    atms: list[ATM]