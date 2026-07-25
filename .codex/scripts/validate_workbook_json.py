from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(path: Path) -> tuple[int, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("sheets"), list):
        raise ValueError("Root must be an object with a sheets array")
    sheets = {}
    for sheet in data["sheets"]:
        if not isinstance(sheet, dict) or not isinstance(sheet.get("name"), str):
            raise ValueError("Every sheet must have a string name")
        if sheet["name"] in sheets:
            raise ValueError(f"Duplicated sheet name: {sheet['name']}")
        if not isinstance(sheet.get("columns"), list) or not all(isinstance(item, str) for item in sheet["columns"]):
            raise ValueError(f"Sheet {sheet['name']!r} columns must be strings")
        if not isinstance(sheet.get("rows"), list) or not all(isinstance(row, dict) for row in sheet["rows"]):
            raise ValueError(f"Sheet {sheet['name']!r} rows must be objects")
        sheets[sheet["name"]] = sheet
    missing = [name for name in ("因子と水準", "テストケース") if name not in sheets]
    if missing:
        raise ValueError(f"Missing required sheets: {', '.join(missing)}")
    factor_columns = sheets["因子と水準"]["columns"]
    missing = [name for name in ("因子", "水準1", "備考") if name not in factor_columns]
    if missing:
        raise ValueError(f"Sheet '因子と水準' is missing columns: {', '.join(missing)}")
    test_sheet = sheets["テストケース"]
    columns = test_sheet["columns"]
    missing = [name for name in ("ID", "expected", "memo") if name not in columns]
    if missing:
        raise ValueError(f"Sheet 'テストケース' is missing columns: {', '.join(missing)}")
    factors = [name for name in columns if name not in {"ID", "expected", "memo"}]
    if not factors:
        raise ValueError("Sheet 'テストケース' must contain at least one factor column")
    seen: set[str] = set()
    unresolved: list[str] = []
    for index, row in enumerate(test_sheet["rows"], start=1):
        missing = [name for name in columns if name not in row]
        if missing:
            raise ValueError(f"Test case row {index} is missing keys: {', '.join(missing)}")
        case_id = row["ID"].strip()
        if not case_id or case_id in seen:
            raise ValueError(f"Empty or duplicated test case ID: {case_id}")
        seen.add(case_id)
        if not row["expected"].strip():
            raise ValueError(f"Test case {case_id} has an empty expected")
        if row["expected"].strip() == "要確認":
            unresolved.append(case_id)
    return len(test_sheet["rows"]), unresolved


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
