from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_schema import REQUIRED_COLUMNS

ALLOWED = {
    "user_type": {"normal", "premium", "blacklisted"},
    "payment": {"credit", "cash"},
    "product": {"normal", "restricted"},
    "expected": {"success", "failed", "forbidden", "blocked"},
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate matrix JSON for PurchaseService.")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("JSON root must be an array")

    ids: set[str] = set()
    errors: list[str] = []

    for idx, row in enumerate(data, start=1):
        if not isinstance(row, dict):
            errors.append(f"Row#{idx}: not an object")
            continue

        for col in REQUIRED_COLUMNS:
            if not row.get(col):
                errors.append(f"Row#{idx}: missing required '{col}'")

        rid = row.get("id")
        if rid:
            if rid in ids:
                errors.append(f"Row#{idx}: duplicated id '{rid}'")
            ids.add(rid)

        for col, choices in ALLOWED.items():
            value = row.get(col)
            if value and value not in choices:
                errors.append(f"Row#{idx}: invalid {col}='{value}'")

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"- {e}")
        raise SystemExit(1)

    print(f"Validation OK: {len(data)} rows")


if __name__ == "__main__":
    main()
