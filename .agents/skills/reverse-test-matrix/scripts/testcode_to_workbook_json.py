from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


METHOD_BLOCK_RE = re.compile(
    r"((?:\s*\[DataRow\([^\]]*\)\]\s*)+)\s*public\s+(?:async\s+)?(?:void|Task(?:<[^>]+>)?)\s+\w+\s*\((.*?)\)",
    flags=re.DOTALL,
)
DATAROW_RE = re.compile(r"\[DataRow\((.*?)\)\]", flags=re.DOTALL)
RESERVED_COLUMNS = {"ID", "expected", "memo"}


def split_top_level_csv(text: str) -> list[str]:
    parts: list[str] = []
    buffer: list[str] = []
    in_string = False
    escaped = False
    depth = 0
    for char in text:
        if in_string:
            buffer.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            buffer.append(char)
        elif char in "([{":
            depth += 1
            buffer.append(char)
        elif char in ")]}":
            depth = max(0, depth - 1)
            buffer.append(char)
        elif char == "," and depth == 0:
            parts.append("".join(buffer).strip())
            buffer = []
        else:
            buffer.append(char)
    if "".join(buffer).strip():
        parts.append("".join(buffer).strip())
    return parts


def parse_literal(token: str) -> str:
    value = token.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace(r'\"', '"').replace(r"\\", "\\")
    if re.fullmatch(r"(?:true|false|null|-?\d+(?:\.\d+)?)(?:[fFdDmMlLuU]*)", value, flags=re.IGNORECASE):
        return value
    raise ValueError(f"Unsupported DataRow literal: {value}")


def normalize_parameter(name: str) -> str:
    compact = re.sub(r"[^a-z0-9]", "", name.lower())
    if compact in {"id", "caseid", "testcaseid", "testid"}:
        return "ID"
    if compact in {"expected", "expectedresult", "result", "actualexpected"}:
        return "expected"
    if compact in {"memo", "note", "remark", "comments"}:
        return "memo"
    return name


def extract_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    for block in METHOD_BLOCK_RE.finditer(text):
        raw_parameters = [item for item in split_top_level_csv(block.group(2)) if item]
        parameter_names = [normalize_parameter(item.split("=")[0].strip().split()[-1]) for item in raw_parameters]
        if len(parameter_names) != len(set(parameter_names)):
            raise ValueError(f"Duplicated normalized parameter in {path}")
        if columns and parameter_names != columns:
            raise ValueError(f"DataRow methods use different parameter columns in {path}")
        columns = parameter_names
        for match in DATAROW_RE.finditer(block.group(1)):
            values = [parse_literal(item) for item in split_top_level_csv(match.group(1))]
            if len(values) != len(parameter_names):
                raise ValueError(
                    f"DataRow argument count does not match method parameters in {path}: "
                    f"{len(values)} != {len(parameter_names)}"
                )
            rows.append(dict(zip(parameter_names, values)))
    return columns, rows


def build_payload(files: list[Path]) -> dict[str, Any]:
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    for path in files:
        file_columns, file_rows = extract_rows(path)
        if not file_rows:
            continue
        if columns and file_columns != columns:
            raise ValueError("Input files use different DataRow parameter columns")
        columns = file_columns
        rows.extend(file_rows)
    if not rows:
        raise ValueError("No supported MSTest DataRow test cases found")

    missing = [name for name in ("ID", "expected") if name not in columns]
    if missing:
        raise ValueError(f"Missing required test parameters: {', '.join(missing)}")
    if "memo" not in columns:
        columns.append("memo")
        for row in rows:
            row["memo"] = ""
    factor_columns = [name for name in columns if name not in RESERVED_COLUMNS]
    if not factor_columns:
        raise ValueError("At least one factor parameter is required")

    seen_ids: set[str] = set()
    for row in rows:
        case_id = row["ID"].strip()
        if not case_id:
            raise ValueError("A test case has an empty ID")
        if case_id in seen_ids:
            raise ValueError(f"Duplicated test case ID: {case_id}")
        seen_ids.add(case_id)
        if not row["expected"].strip():
            raise ValueError(f"Test case {case_id} has an empty expected")

    max_levels = max(len(dict.fromkeys(row[name] for row in rows)) for name in factor_columns)
    factor_sheet_columns = ["因子", *[f"水準{index}" for index in range(1, max_levels + 1)], "備考"]
    factor_rows = []
    for name in factor_columns:
        levels = list(dict.fromkeys(row[name] for row in rows))
        factor_row = {column: "" for column in factor_sheet_columns}
        factor_row["因子"] = name
        factor_row["備考"] = "既存DataRowに現れる値から復元"
        for index, level in enumerate(levels, start=1):
            factor_row[f"水準{index}"] = level
        factor_rows.append(factor_row)

    return {
        "sheets": [
            {"name": "因子と水準", "columns": factor_sheet_columns, "rows": factor_rows},
            {"name": "テストケース", "columns": columns, "rows": rows},
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Reverse MSTest DataRow tests to workbook JSON.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    target = Path(args.input)
    if target.is_dir():
        files = sorted(path for path in target.rglob("*.cs") if path.is_file())
    elif target.is_file() and target.suffix.lower() == ".cs":
        files = [target]
    else:
        raise ValueError(f"Input must be an existing .cs file or directory: {target}")
    if not files:
        raise ValueError(f"No .cs files found under: {target}")

    output = Path(args.output)
    if output.parent.name != "testcases" or not output.name.startswith("testcase_") or output.suffix.lower() != ".json":
        raise ValueError("Output must be named testcases/testcase_*.json")
    payload = build_payload(files)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    factor_count = len(payload["sheets"][0]["rows"])
    case_count = len(payload["sheets"][1]["rows"])
    print(f"Reversed {len(files)} files / {factor_count} factors / {case_count} cases -> {output}")


if __name__ == "__main__":
    main()
