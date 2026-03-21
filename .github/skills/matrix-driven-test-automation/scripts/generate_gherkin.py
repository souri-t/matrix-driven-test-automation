from __future__ import annotations

import argparse
import json
from pathlib import Path

from matrix_schema import REQUIRED_COLUMNS


def collect_headers(rows: list[dict[str, object]]) -> list[str]:
    headers: list[str] = []
    for row in rows:
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
    parser = argparse.ArgumentParser(description="Generate Gherkin from matrix JSON.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not rows:
        raise ValueError("No test cases found")
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("Each JSON row must be an object")

    headers = collect_headers(rows)
    input_headers = [h for h in headers if h not in ("id", "expected", "memo")]

    steps = ['    When テスト対象を実行する']
    if input_headers:
        first = input_headers[0]
        steps = [f'    Given 入力 "{first}" が "<{first}>"']
        steps.extend([f'    And 入力 "{h}" が "<{h}>"' for h in input_headers[1:]])
        steps.append("    When テスト対象を実行する")

    lines = [
        "Feature: Matrix Driven Test",
        "",
        "  Scenario Outline: ケース <id>",
        *steps,
        '    Then 期待値が "<expected>" である',
        "",
        "    Examples:",
        "      | " + " | ".join(headers) + " |",
    ]

    for row in rows:
        values = [str(row.get(k, "")).replace("|", "\\|") for k in headers]
        lines.append("      | " + " | ".join(values) + " |")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Generated: {output}")


if __name__ == "__main__":
    main()
