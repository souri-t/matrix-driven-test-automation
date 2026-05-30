from __future__ import annotations

REQUIRED_COLUMNS = ["id", "expected", "memo"]


def normalize_column_name(name: str) -> str:
    if name == "ID":
        return "id"
    return name.strip()


def denormalize_column_name(name: str) -> str:
    if name == "id":
        return "ID"
    return name
