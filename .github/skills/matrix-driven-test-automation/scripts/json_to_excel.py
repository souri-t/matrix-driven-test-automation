from __future__ import annotations

import argparse
import json
from pathlib import Path

from openpyxl import Workbook

from matrix_schema import REQUIRED_COLUMNS, denormalize_column_name


def collect_headers(data: list[dict[str, object]]) -> list[str]:
    if not data:
        return REQUIRED_COLUMNS.copy()

    headers: list[str] = []
    for row in data:
        for key in row.keys():
            if key not in headers:
                headers.append(key)

    for key in REQUIRED_COLUMNS:
        if key not in headers:
            headers.append(key)

    if "id" in headers:
        headers.remove("id")
        headers.insert(0, "id")
    if "expected" in headers:
        headers.remove("expected")
        headers.append("expected")
    if "memo" in headers:
        headers.remove("memo")
        headers.append("memo")

    return headers


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert matrix JSON to Excel.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("JSON root must be an array")
    if any(not isinstance(row, dict) for row in data):
        raise ValueError("Each JSON row must be an object")

    wb = Workbook()
    ws = wb.active
    ws.title = "matrix"

    headers = collect_headers(data)
    ws.append([denormalize_column_name(c) for c in headers])
    for row in data:
        ws.append([row.get(c, "") for c in headers])

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)

    print(f"Converted {len(data)} cases -> {output}")


if __name__ == "__main__":
    main()
