from __future__ import annotations

import json
from pathlib import Path


EN_PATH = Path("branches.json")
AM_PATH = Path("brancham.json")
OM_PATH = Path("branchor.json")
OUTPUT_PATH = Path("app/seed/branches_merged.json")

# Map inconsistent source IDs to one canonical ID
ID_ALIASES = {
    "shashemane_arada": "shashemene_arada",
}


def normalize_id(branch_id: str) -> str:
    return ID_ALIASES.get(branch_id, branch_id)


def load_branches(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    normalized: dict[str, dict] = {}

    for branch in data["branches"]:
        branch_copy = dict(branch)
        branch_copy["id"] = normalize_id(branch["id"])
        normalized[branch_copy["id"]] = branch_copy

    return normalized


def get_value(entry: dict | None, key: str, default=""):
    if entry is None:
        return default
    return entry.get(key, default)


def choose_base(*entries: dict | None) -> dict:
    for entry in entries:
        if entry is not None:
            return entry
    raise ValueError("No base entry found.")


def main() -> None:
    en_branches = load_branches(EN_PATH)
    am_branches = load_branches(AM_PATH)
    om_branches = load_branches(OM_PATH)

    all_ids = sorted(set(en_branches) | set(am_branches) | set(om_branches))

    merged_branches = []
    missing_report = []
    mismatch_report = []

    for branch_id in all_ids:
        en = en_branches.get(branch_id)
        am = am_branches.get(branch_id)
        om = om_branches.get(branch_id)

        if not (en and am and om):
            missing_report.append(
                {
                    "id": branch_id,
                    "missing_en": en is None,
                    "missing_am": am is None,
                    "missing_om": om is None,
                }
            )

        base = choose_base(en, am, om)

        for field in ("plus_code", "latitude", "longitude"):
            values = {
                entry[field]
                for entry in (en, am, om)
                if entry is not None and field in entry
            }
            if len(values) > 1:
                mismatch_report.append(
                    {
                        "id": branch_id,
                        "field": field,
                        "values": list(values),
                    }
                )

        merged_branches.append(
            {
                "id": branch_id,
                "name": {
                    "en": get_value(en, "name"),
                    "am": get_value(am, "name"),
                    "om": get_value(om, "name"),
                },
                "city": {
                    "en": get_value(en, "city"),
                    "am": get_value(am, "city"),
                    "om": get_value(om, "city"),
                },
                "region": {
                    "en": get_value(en, "region"),
                    "am": get_value(am, "region"),
                    "om": get_value(om, "region"),
                },
                "address": {
                    "en": get_value(en, "address"),
                    "am": get_value(am, "address"),
                    "om": get_value(om, "address"),
                },
                "plus_code": get_value(base, "plus_code"),
                "latitude": get_value(base, "latitude"),
                "longitude": get_value(base, "longitude"),
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump({"branches": merged_branches}, f, ensure_ascii=False, indent=2)

    print(f"Merged {len(merged_branches)} branches into {OUTPUT_PATH}")

    if missing_report:
        print("\nMissing language entries:")
        for item in missing_report[:20]:
            print(item)
    else:
        print("\nNo missing language entries found.")

    if mismatch_report:
        print("\nCoordinate/plus_code mismatches:")
        for item in mismatch_report[:20]:
            print(item)
    else:
        print("\nNo coordinate or plus_code mismatches found.")


if __name__ == "__main__":
    main()