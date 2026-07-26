from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_SHEET_ORDER = ("テスト対象", "因子と水準", "テストケース")
REQUIRED_TARGET_COLUMNS = ("テスト対象", "根拠資料", "参照箇所", "参照目的", "備考")
REQUIRED_FACTOR_COLUMNS = ("因子", "水準", "備考")


def _validate_sheet_shape(sheet: Any, seen_names: set[str]) -> None:
    if not isinstance(sheet, dict) or not isinstance(sheet.get("name"), str):
        raise ValueError("Every sheet must have a string name")
    name = sheet["name"]
    if name in seen_names:
        raise ValueError(f"Duplicated sheet name: {name}")
    seen_names.add(name)
    columns = sheet.get("columns")
    if not isinstance(columns, list) or not all(isinstance(item, str) for item in columns):
        raise ValueError(f"Sheet {name!r} columns must be strings")
    if any(not item for item in columns):
        raise ValueError(f"Sheet {name!r} has an empty column name")
    if len(columns) != len(set(columns)):
        raise ValueError(f"Sheet {name!r} has duplicated columns")
    rows = sheet.get("rows")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"Sheet {name!r} rows must be objects")
    for index, row in enumerate(rows, start=1):
        missing = [column for column in columns if column not in row]
        extra = [key for key in row if key not in columns]
        if missing:
            raise ValueError(
                f"Sheet {name!r} row {index} is missing keys: {', '.join(missing)}"
            )
        if extra:
            raise ValueError(
                f"Sheet {name!r} row {index} has unexpected keys: {', '.join(extra)}"
            )
        if not all(isinstance(row[column], str) for column in columns):
            raise ValueError(f"Sheet {name!r} row {index} values must be strings")


def validate_payload(data: Any) -> tuple[int, list[str]]:
    if not isinstance(data, dict) or not isinstance(data.get("sheets"), list):
        raise ValueError("Root must be an object with a sheets array")

    seen_names: set[str] = set()
    for sheet in data["sheets"]:
        _validate_sheet_shape(sheet, seen_names)

    actual_order = tuple(sheet["name"] for sheet in data["sheets"])
    if actual_order != REQUIRED_SHEET_ORDER:
        raise ValueError(
            "Workbook sheets must be exactly, in order: "
            + ", ".join(REQUIRED_SHEET_ORDER)
        )
    sheets = {sheet["name"]: sheet for sheet in data["sheets"]}

    target_sheet = sheets["テスト対象"]
    if tuple(target_sheet["columns"]) != REQUIRED_TARGET_COLUMNS:
        raise ValueError(
            "Sheet 'テスト対象' columns must be exactly, in order: "
            + ", ".join(REQUIRED_TARGET_COLUMNS)
        )
    if not target_sheet["rows"]:
        raise ValueError("Sheet 'テスト対象' must contain at least one row")
    for index, row in enumerate(target_sheet["rows"], start=1):
        if not row["テスト対象"].strip():
            raise ValueError(f"Test target row {index} has an empty テスト対象")

    factor_sheet = sheets["因子と水準"]
    if tuple(factor_sheet["columns"]) != REQUIRED_FACTOR_COLUMNS:
        raise ValueError(
            "Sheet '因子と水準' columns must be exactly, in order: "
            + ", ".join(REQUIRED_FACTOR_COLUMNS)
        )
    if not factor_sheet["rows"]:
        raise ValueError("Sheet '因子と水準' must contain at least one row")
    factor_order: list[str] = []
    levels_by_factor: dict[str, set[str]] = {}
    seen_levels: set[tuple[str, str]] = set()
    for index, row in enumerate(factor_sheet["rows"], start=1):
        factor = row["因子"].strip()
        level = row["水準"].strip()
        if not factor:
            raise ValueError(f"Factor level row {index} has an empty 因子")
        if not level:
            raise ValueError(f"Factor level row {index} has an empty 水準")
        key = (factor, level)
        if key in seen_levels:
            raise ValueError(f"Duplicated 因子 and 水準: {factor} / {level}")
        seen_levels.add(key)
        if factor not in levels_by_factor:
            factor_order.append(factor)
            levels_by_factor[factor] = set()
        levels_by_factor[factor].add(level)

    test_sheet = sheets["テストケース"]
    columns = test_sheet["columns"]
    if (
        len(columns) < 5
        or columns[:2] != ["ID", "テストの目的"]
        or columns[-2:] != ["expected", "memo"]
    ):
        raise ValueError(
            "Sheet 'テストケース' columns must be, in order: "
            "ID, テストの目的, one or more factor columns, expected, memo"
        )
    factors = columns[2:-2]
    if factors != factor_order:
        raise ValueError(
            "Test case factor columns must match factor order: "
            + ", ".join(factor_order)
        )
    if not test_sheet["rows"]:
        raise ValueError("Sheet 'テストケース' must contain at least one row")

    seen_ids: set[str] = set()
    unresolved: list[str] = []
    used_levels: set[tuple[str, str]] = set()
    for index, row in enumerate(test_sheet["rows"], start=1):
        case_id = row["ID"].strip()
        if not case_id or case_id in seen_ids:
            raise ValueError(f"Empty or duplicated test case ID: {case_id}")
        seen_ids.add(case_id)
        if not row["テストの目的"].strip():
            raise ValueError(f"Test case {case_id} has an empty テストの目的")
        expected = row["expected"].strip()
        if not expected:
            raise ValueError(f"Test case {case_id} has an empty expected")
        if expected == "要確認":
            unresolved.append(case_id)
        for factor in factors:
            level = row[factor].strip()
            if level not in levels_by_factor[factor]:
                raise ValueError(
                    f"Test case {case_id} uses undefined level: {factor} / {level}"
                )
            used_levels.add((factor, level))

    unused_levels = [
        f"{row['因子'].strip()} / {row['水準'].strip()}"
        for row in factor_sheet["rows"]
        if (row["因子"].strip(), row["水準"].strip()) not in used_levels
    ]
    if unused_levels:
        raise ValueError("Unused factor levels: " + ", ".join(unused_levels))
    return len(test_sheet["rows"]), unresolved


def validate(path: Path) -> tuple[int, list[str]]:
    return validate_payload(json.loads(path.read_text(encoding="utf-8")))


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate workbook test matrix JSON.")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    path = Path(args.input)
    if not path.is_file():
        raise ValueError(f"Input JSON not found: {path}")
    if (
        path.parent.name != "testcases"
        or not path.name.startswith("testcase_")
        or path.suffix.lower() != ".json"
    ):
        raise ValueError("Input must be named testcases/testcase_*.json")
    count, unresolved = validate(path)
    if unresolved:
        raise ValueError(f"Unresolved expected values: {', '.join(unresolved)}")
    print(f"Valid workbook JSON: {count} test cases -> {path}")


if __name__ == "__main__":
    main()
