from __future__ import annotations

import argparse
import json
from pathlib import Path


HEADERS = ["id", "user_type", "payment", "product", "expected"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Gherkin from matrix JSON.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not rows:
        raise ValueError("No test cases found")

    lines = [
        "Feature: 商品購入",
        "",
        "  Scenario Outline: 商品購入 <id>",
        "    Given ユーザー種別が \"<user_type>\"",
        "    And 支払い方法が \"<payment>\"",
        "    And 商品種別が \"<product>\"",
        "    When 商品を購入する",
        "    Then 結果が \"<expected>\" である",
        "",
        "    Examples:",
        "      | " + " | ".join(HEADERS) + " |",
    ]

    for row in rows:
        values = [str(row.get(k, "")).replace("|", "\\|") for k in HEADERS]
        lines.append("      | " + " | ".join(values) + " |")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Generated: {output}")


if __name__ == "__main__":
    main()
