from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from app.schemas.branch import Branch, BranchDataset
from app.services.geo_service import haversine_distance_km


BRANCH_FILE_PATH = Path("app/seed/branches_merged.json")


def normalize_text(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"\s+", " ", value)
    return value


@lru_cache(maxsize=1)
def load_branch_dataset() -> BranchDataset:
    with BRANCH_FILE_PATH.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    return BranchDataset.model_validate(raw_data)


def get_all_branches() -> list[Branch]:
    return load_branch_dataset().branches


def _localized_values(branch: Branch) -> dict[str, list[str]]:
    return {
        "name": list(branch.name.model_dump().values()),
        "city": list(branch.city.model_dump().values()),
        "region": list(branch.region.model_dump().values()),
        "address": list(branch.address.model_dump().values()),
        "plus_code": [branch.plus_code] if branch.plus_code else [],
    }


def _branch_match_score(branch: Branch, query: str) -> int:
    query = normalize_text(query)
    fields = _localized_values(branch)

    score = 0

    for value in fields["name"]:
        normalized = normalize_text(value)
        if query == normalized:
            score = max(score, 120)
        elif query in normalized:
            score = max(score, 100)

    for field_name in ("city", "region"):
        for value in fields[field_name]:
            normalized = normalize_text(value)
            if query == normalized:
                score = max(score, 90)
            elif query in normalized:
                score = max(score, 75)

    for field_name in ("address", "plus_code"):
        for value in fields[field_name]:
            normalized = normalize_text(value)
            if query in normalized:
                score = max(score, 55)

    return score


def search_branches(query: str, limit: int = 5) -> list[Branch]:
    query = normalize_text(query)
    if not query:
        return []

    scored: list[tuple[int, Branch]] = []

    for branch in get_all_branches():
        score = _branch_match_score(branch, query)
        if score > 0:
            scored.append((score, branch))

    scored.sort(key=lambda item: (-item[0], item[1].name.en))
    return [branch for _, branch in scored[:limit]]


def get_nearest_branches(
    latitude: float,
    longitude: float,
    limit: int = 5,
) -> list[tuple[Branch, float]]:
    ranked: list[tuple[Branch, float]] = []

    for branch in get_all_branches():
        distance = haversine_distance_km(
            latitude,
            longitude,
            branch.latitude,
            branch.longitude,
        )
        ranked.append((branch, distance))

    ranked.sort(key=lambda item: item[1])
    return ranked[:limit]