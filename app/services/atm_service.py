from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from app.schemas.atm import ATM, ATMDataset
from app.services.geo_service import haversine_distance_km


ATM_FILE_PATH = Path("app/seed/atms_merged.json")


def normalize_text(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"\s+", " ", value)
    return value


@lru_cache(maxsize=1)
def load_atm_dataset() -> ATMDataset:
    with ATM_FILE_PATH.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    return ATMDataset.model_validate(raw_data)


def get_all_atms() -> list[ATM]:
    return [atm for atm in load_atm_dataset().atms if atm.is_active]


def _localized_values(atm: ATM) -> dict[str, list[str]]:
    return {
        "name": list(atm.name.model_dump().values()),
        "location": list(atm.location.model_dump().values()),
        "desc": list(atm.desc.model_dump().values()),
    }


def _atm_match_score(atm: ATM, query: str) -> int:
    query = normalize_text(query)
    fields = _localized_values(atm)

    score = 0

    for value in fields["name"]:
        normalized = normalize_text(value)
        if query == normalized:
            score = max(score, 120)
        elif query in normalized:
            score = max(score, 100)

    for field_name in ("location", "desc"):
        for value in fields[field_name]:
            normalized = normalize_text(value)
            if query == normalized:
                score = max(score, 90)
            elif query in normalized:
                score = max(score, 70)

    return score


def search_atms(query: str, limit: int = 5) -> list[ATM]:
    query = normalize_text(query)
    if not query:
        return []

    scored: list[tuple[int, ATM]] = []

    for atm in get_all_atms():
        score = _atm_match_score(atm, query)
        if score > 0:
            scored.append((score, atm))

    scored.sort(key=lambda item: (-item[0], item[1].name.en))
    return [atm for _, atm in scored[:limit]]


def get_nearest_atms(
    latitude: float,
    longitude: float,
    limit: int = 5,
) -> list[tuple[ATM, float]]:
    ranked: list[tuple[ATM, float]] = []

    for atm in get_all_atms():
        if atm.latitude == 0.0 and atm.longitude == 0.0:
            continue

        distance = haversine_distance_km(
            latitude,
            longitude,
            atm.latitude,
            atm.longitude,
        )
        ranked.append((atm, distance))

    ranked.sort(key=lambda item: item[1])
    return ranked[:limit]