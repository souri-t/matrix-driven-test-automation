from __future__ import annotations

import argparse
from itertools import product
from pathlib import Path

from openpyxl import Workbook


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a sample Excel matrix for ramen ticket combinations.")
    parser.add_argument("--output", default="testcases/purchase_matrix.xlsx")
    args = parser.parse_args()

    soups = ["塩", "醤油", "味噌"]
    noodle_thickness = ["細麺", "太麺"]
    noodle_amount = ["普通", "大盛り"]

    rows = [
        ["ID", "スープ", "麺の太さ", "麺の量", "expected", "memo"],
    ]

    combinations = product(soups, noodle_thickness, noodle_amount)
    for index, (soup, thickness, amount) in enumerate(combinations, start=1):
        rows.append(
            [
                f"TC{index:03}",
                soup,
                thickness,
                amount,
                f"食券{index}",
                "組み合わせ確認",
            ]
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "matrix"

    for row in rows:
        ws.append(row)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)

    print(f"Created: {output}")


if __name__ == "__main__":
    main()
