from __future__ import annotations

import argparse
from pathlib import Path

from openpyxl import Workbook


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a sample Excel matrix for PurchaseService.")
    parser.add_argument("--output", default="testcases/purchase_matrix.xlsx")
    args = parser.parse_args()

    rows = [
        ["ID", "user_type", "payment", "product", "expected", "memo"],
        ["TC001", "normal", "credit", "normal", "success", "基本パス"],
        ["TC002", "normal", "cash", "normal", "success", "現金決済"],
        ["TC003", "normal", "cash", "restricted", "forbidden", "制限商品"],
        ["TC004", "premium", "cash", "restricted", "failed", "仕様確認ケース"],
        ["TC005", "blacklisted", "credit", "normal", "blocked", "ブラックリスト"],
    ]

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
