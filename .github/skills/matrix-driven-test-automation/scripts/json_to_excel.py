from __future__ import annotations

import argparse
import json
from pathlib import Path

from openpyxl import Workbook

from matrix_schema import REQUIRED_COLUMNS, denormalize_column_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert matrix JSON to Excel.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("JSON root must be an array")

    wb = Workbook()
    ws = wb.active
    ws.title = "matrix"

    ws.append([denormalize_column_name(c) for c in REQUIRED_COLUMNS])
    for row in data:
        ws.append([row.get(c, "") for c in REQUIRED_COLUMNS])

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)

    print(f"Converted {len(data)} cases -> {output}")


if __name__ == "__main__":
    main()
