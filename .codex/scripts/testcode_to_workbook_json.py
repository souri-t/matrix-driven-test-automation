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
    tail = "".join(buffer).strip()
    if tail:
        parts.append(tail)
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
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    for block in METHOD_BLOCK_RE.finditer(path.read_text(encoding="utf-8")):
        parameters = [item for item in split_top_level_csv(block.group(2)) if item]
        names = [normalize_parameter(item.split("=")[0].strip().split()[-1]) for item in parameters]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicated normalized parameter in {path}")
        if columns and names != columns:
            raise ValueError(f"DataRow methods use different parameter columns in {path}")
        columns = names
        for match in DATAROW_RE.finditer(block.group(1)):
            values = [parse_literal(item) for item in split_top_level_csv(match.group(1))]
            if len(values) != len(names):
                raise ValueError(f"DataRow argument count does not match method parameters in {path}")
            rows.append(dict(zip(names, values)))
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
    factors = [name for name in columns if name not in RESERVED_COLUMNS]
    if not factors:
        raise ValueError("At least one factor parameter is required")
    seen: set[str] = set()
    for row in rows:
        case_id = row["ID"].strip()
        if not case_id:
            raise ValueError("A test case has an empty ID")
        if case_id in seen:
            raise ValueError(f"Duplicated test case ID: {case_id}")
        seen.add(case_id)
        if not row["expected"].strip():
            raise ValueError(f"Test case {case_id} has an empty expected")
    factor_columns = ["因子", "水準", "備考"]
    factor_rows: list[dict[str, str]] = []
    for name in factors:
        for level in dict.fromkeys(row[name] for row in rows):
            factor_rows.append(
                {
                    "因子": name,
                    "水準": level,
                    "備考": "既存DataRowに現れる値から復元",
                }
            )
    return {"sheets": [
        {"name": "因子と水準", "columns": factor_columns, "rows": factor_rows},
        {"name": "テストケース", "columns": columns, "rows": rows},
    ]}


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
    factor_count = len({row["因子"] for row in payload["sheets"][0]["rows"]})
    print(f"Reversed {len(files)} files / {factor_count} factors / {len(payload['sheets'][1]['rows'])} cases -> {output}")


if __name__ == "__main__":
    main()
