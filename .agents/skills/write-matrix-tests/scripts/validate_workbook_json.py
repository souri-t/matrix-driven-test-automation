from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_SHEETS = ("因子と水準", "テストケース")
RESERVED_TEST_COLUMNS = {"ID", "expected", "memo"}


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be an array of strings")
    return value


def validate(path: Path) -> tuple[int, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("sheets"), list):
        raise ValueError("Root must be an object with a sheets array")

    sheets: dict[str, dict[str, Any]] = {}
    for index, sheet in enumerate(data["sheets"], start=1):
        if not isinstance(sheet, dict) or not isinstance(sheet.get("name"), str):
            raise ValueError(f"sheets[{index}] must have a string name")
        if sheet["name"] in sheets:
            raise ValueError(f"Duplicated sheet name: {sheet['name']}")
        require_string_list(sheet.get("columns"), f"Sheet {sheet['name']!r} columns")
        if not isinstance(sheet.get("rows"), list) or not all(isinstance(row, dict) for row in sheet["rows"]):
            raise ValueError(f"Sheet {sheet['name']!r} rows must be an array of objects")
        sheets[sheet["name"]] = sheet

    missing_sheets = [name for name in REQUIRED_SHEETS if name not in sheets]
    if missing_sheets:
        raise ValueError(f"Missing required sheets: {', '.join(missing_sheets)}")

    factor_sheet_columns = sheets["因子と水準"]["columns"]
    missing_factor_columns = [name for name in ("因子", "水準1", "備考") if name not in factor_sheet_columns]
    if missing_factor_columns:
        raise ValueError(f"Sheet '因子と水準' is missing columns: {', '.join(missing_factor_columns)}")

    testcase_sheet = sheets["テストケース"]
    columns = testcase_sheet["columns"]
    missing_columns = [name for name in ("ID", "expected", "memo") if name not in columns]
    if missing_columns:
        raise ValueError(f"Sheet 'テストケース' is missing columns: {', '.join(missing_columns)}")
    factor_columns = [name for name in columns if name not in RESERVED_TEST_COLUMNS]
    if not factor_columns:
        raise ValueError("Sheet 'テストケース' must contain at least one factor column")

    seen_ids: set[str] = set()
    unresolved: list[str] = []
    for index, row in enumerate(testcase_sheet["rows"], start=1):
        missing_keys = [name for name in columns if name not in row]
        if missing_keys:
            raise ValueError(f"Test case row {index} is missing keys: {', '.join(missing_keys)}")
        if not all(isinstance(row[name], str) for name in columns):
            raise ValueError(f"Test case row {index} values must be strings")
        case_id = row["ID"].strip()
        if not case_id:
            raise ValueError(f"Test case row {index} has an empty ID")
        if case_id in seen_ids:
            raise ValueError(f"Duplicated test case ID: {case_id}")
        seen_ids.add(case_id)
        if not row["expected"].strip():
            raise ValueError(f"Test case {case_id} has an empty expected")
        if row["expected"].strip() == "要確認":
            unresolved.append(case_id)

    return len(testcase_sheet["rows"]), unresolved


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate workbook test matrix JSON.")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    path = Path(args.input)
    if not path.is_file():
        raise ValueError(f"Input JSON not found: {path}")
    if path.parent.name != "testcases" or not path.name.startswith("testcase_") or path.suffix.lower() != ".json":
        raise ValueError("Input must be named testcases/testcase_*.json")
    count, unresolved = validate(path)
    if unresolved:
        raise ValueError(f"Unresolved expected values: {', '.join(unresolved)}")
    print(f"Valid workbook JSON: {count} test cases -> {path}")


if __name__ == "__main__":
    main()
