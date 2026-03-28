from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from project_context import infer_project_context


METHOD_BLOCK_RE = re.compile(
    r"((?:\s*\[DataRow\([^\]]*\)\]\s*)+)\s*public\s+void\s+\w+\s*\((.*?)\)",
    flags=re.DOTALL,
)
DATAROW_RE = re.compile(r"\[DataRow\((.*?)\)\]", flags=re.DOTALL)


def split_top_level_csv(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    in_string = False
    escaped = False
    depth = 0

    for ch in text:
        if in_string:
            buf.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            buf.append(ch)
            continue

        if ch in "([{":
            depth += 1
            buf.append(ch)
            continue

        if ch in ")]}":
            depth = max(0, depth - 1)
            buf.append(ch)
            continue

        if ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
            continue

        buf.append(ch)

    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def parse_csharp_literal(token: str) -> str:
    t = token.strip()
    if t.startswith('"') and t.endswith('"') and len(t) >= 2:
        inner = t[1:-1]
        inner = inner.replace(r'\"', '"').replace(r"\\", "\\")
        return inner
    if t.lower() in {"true", "false"}:
        return t.lower()
    return t


def to_snake_case(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.replace("-", "_").strip("_").lower()


def normalize_key(name: str) -> str:
    base = to_snake_case(name)
    compact = base.replace("_", "")

    if compact in {"id", "caseid", "testcaseid", "testid"}:
        return "id"
    if compact in {"expected", "expectedresult", "result", "actualexpected"}:
        return "expected"
    if compact in {"memo", "note", "remark", "comments"}:
        return "memo"
    return base


def extract_rows_from_file(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []

    for block in METHOD_BLOCK_RE.finditer(text):
        attrs = block.group(1)
        params = block.group(2)

        raw_params = [p.strip() for p in split_top_level_csv(params) if p.strip()]
        if not raw_params:
            continue

        param_names = [normalize_key(p.split()[-1]) for p in raw_params]

        for m in DATAROW_RE.finditer(attrs):
            args = [parse_csharp_literal(x) for x in split_top_level_csv(m.group(1))]
            if len(args) != len(param_names):
                continue

            row = {k: v for k, v in zip(param_names, args)}
            if "memo" not in row:
                row["memo"] = ""
            rows.append(row)

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create matrix JSON from existing test code (reverse conversion)."
    )
    parser.add_argument(
        "--input",
        default="",
        help="Optional test code file or directory. If omitted, infer from current project.",
    )
    parser.add_argument("--output", default="testcases/reversed_matrix.json")
    args = parser.parse_args()

    context = infer_project_context()
    if context.language != "csharp" or context.test_framework != "mstest":
        raise ValueError(
            f"Current reverse conversion supports csharp/mstest only (inferred: {context.language}/{context.test_framework})."
        )

    if args.input:
        target = Path(args.input)
    else:
        default_file = context.generated_test_file
        target = default_file if default_file.exists() else context.test_project_path.parent / "Generated"

    files: list[Path]
    if target.is_dir():
        files = sorted(p for p in target.rglob("*.cs") if p.is_file())
    elif target.is_file():
        files = [target]
    else:
        raise ValueError(f"Input not found: {target}")

    if not files:
        raise ValueError(f"No .cs files found under: {target}")

    rows: list[dict[str, str]] = []
    for f in files:
        rows.extend(extract_rows_from_file(f))

    if not rows:
        raise ValueError("No DataRow-based test cases found.")

    ids: set[str] = set()
    for i, row in enumerate(rows, start=1):
        if not row.get("id"):
            raise ValueError(f"Row#{i} has no id")
        if row["id"] in ids:
            raise ValueError(f"Duplicated id found while reversing: {row['id']}")
        ids.add(row["id"])
        if "expected" not in row or row["expected"] == "":
            raise ValueError(f"Row#{i} has no expected value")
        if "memo" not in row:
            row["memo"] = ""

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Reversed {len(rows)} cases -> {output}")


if __name__ == "__main__":
    main()
