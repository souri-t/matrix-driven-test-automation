from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from validate_workbook_json import validate_payload


METHOD_BLOCK_RE = re.compile(
    r"((?:\s*\[DataRow\([^\]]*\)\]\s*)+)\s*public\s+(?:async\s+)?"
    r"(?:void|Task(?:<[^>]+>)?)\s+(\w+)\s*\((.*?)\)",
    flags=re.DOTALL,
)
DATAROW_RE = re.compile(r"\[DataRow\((.*?)\)\]", flags=re.DOTALL)
RESERVED_COLUMNS = {"ID", "テストの目的", "expected", "memo"}


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
    if compact in {"purpose", "testpurpose", "description", "testdescription"}:
        return "テストの目的"
    if compact in {"expected", "expectedresult", "result", "actualexpected"}:
        return "expected"
    if compact in {"memo", "note", "remark", "comments"}:
        return "memo"
    return name


def extract_rows(path: Path) -> tuple[list[str], list[dict[str, str]], list[str]]:
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    methods: list[str] = []
    for block in METHOD_BLOCK_RE.finditer(path.read_text(encoding="utf-8")):
        method_name = block.group(2)
        parameters = [item for item in split_top_level_csv(block.group(3)) if item]
        names = [normalize_parameter(item.split("=")[0].strip().split()[-1]) for item in parameters]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicated normalized parameter in {path}")
        if columns and names != columns:
            raise ValueError(f"DataRow methods use different parameter columns in {path}")
        columns = names
        methods.append(method_name)
        for match in DATAROW_RE.finditer(block.group(1)):
            values = [parse_literal(item) for item in split_top_level_csv(match.group(1))]
            if len(values) != len(names):
                raise ValueError(f"DataRow argument count does not match method parameters in {path}")
            rows.append(dict(zip(names, values)))
    return columns, rows, methods


def validate_enrichment(enrichment: Any) -> tuple[str, dict[str, str]]:
    if not isinstance(enrichment, dict):
        raise ValueError("Enrichment must be a JSON object")
    target = enrichment.get("テスト対象")
    if not isinstance(target, str) or not target.strip():
        raise ValueError("Enrichment must contain a non-empty テスト対象")
    purposes = enrichment.get("テストの目的")
    if not isinstance(purposes, dict) or not all(
        isinstance(case_id, str) and isinstance(purpose, str)
        for case_id, purpose in purposes.items()
    ):
        raise ValueError("Enrichment テストの目的 must be an object of ID and text")
    return target, purposes


def build_payload(files: list[Path], enrichment: dict[str, Any]) -> dict[str, Any]:
    test_target, purposes = validate_enrichment(enrichment)
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    source_rows: list[dict[str, str]] = []
    for path in files:
        file_columns, file_rows, methods = extract_rows(path)
        if not file_rows:
            continue
        if columns and file_columns != columns:
            raise ValueError("Input files use different DataRow parameter columns")
        columns = file_columns
        rows.extend(file_rows)
        source_rows.append(
            {
                "テスト対象": test_target,
                "根拠資料": path.as_posix(),
                "参照箇所": "DataRowメソッド: " + ", ".join(methods),
                "参照目的": "既存テストケースの復元",
                "備考": "",
            }
        )
    if not rows:
        raise ValueError("No supported MSTest DataRow test cases found")
    missing = [name for name in ("ID", "expected") if name not in columns]
    if missing:
        raise ValueError(f"Missing required test parameters: {', '.join(missing)}")
    factors = [name for name in columns if name not in RESERVED_COLUMNS]
    if not factors:
        raise ValueError("At least one factor parameter is required")
    seen: set[str] = set()
    normalized_rows: list[dict[str, str]] = []
    for row in rows:
        case_id = row["ID"].strip()
        if not case_id:
            raise ValueError("A test case has an empty ID")
        if case_id in seen:
            raise ValueError(f"Duplicated test case ID: {case_id}")
        seen.add(case_id)
        if not row["expected"].strip():
            raise ValueError(f"Test case {case_id} has an empty expected")
        purpose = purposes.get(case_id, row.get("テストの目的", "")).strip()
        if not purpose:
            raise ValueError(f"Enrichment is missing テストの目的 for {case_id}")
        normalized_rows.append(
            {
                "ID": case_id,
                "テストの目的": purpose,
                **{factor: row[factor] for factor in factors},
                "expected": row["expected"],
                "memo": row.get("memo", ""),
            }
        )
    unknown_purpose_ids = [case_id for case_id in purposes if case_id not in seen]
    if unknown_purpose_ids:
        raise ValueError(
            "Enrichment contains unknown test case IDs: "
            + ", ".join(unknown_purpose_ids)
        )
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
    payload = {
        "sheets": [
            {
                "name": "テスト対象",
                "columns": ["テスト対象", "根拠資料", "参照箇所", "参照目的", "備考"],
                "rows": source_rows,
            },
            {"name": "因子と水準", "columns": factor_columns, "rows": factor_rows},
            {
                "name": "テストケース",
                "columns": ["ID", "テストの目的", *factors, "expected", "memo"],
                "rows": normalized_rows,
            },
        ]
    }
    validate_payload(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Reverse MSTest DataRow tests to workbook JSON.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--enrichment", required=True)
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
    enrichment_path = Path(args.enrichment)
    if not enrichment_path.is_file():
        raise ValueError(f"Enrichment JSON not found: {enrichment_path}")
    enrichment = json.loads(enrichment_path.read_text(encoding="utf-8"))
    output = Path(args.output)
    if output.parent.name != "testcases" or not output.name.startswith("testcase_") or output.suffix.lower() != ".json":
        raise ValueError("Output must be named testcases/testcase_*.json")
    payload = build_payload(files, enrichment)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    source_count = len(payload["sheets"][0]["rows"])
    factor_count = len({row["因子"] for row in payload["sheets"][1]["rows"]})
    print(
        f"Reversed {source_count} files / {factor_count} factors / "
        f"{len(payload['sheets'][2]['rows'])} cases -> {output}"
    )


if __name__ == "__main__":
    main()
