from __future__ import annotations

import argparse
from pathlib import Path

from openpyxl import Workbook


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a sample Excel matrix for PurchaseService.")
    parser.add_argument("--output", default="testcases/purchase_matrix.xlsx")
    args = parser.parse_args()

    rows = [
        ["ID", "user_type", "payment", "product", "expected"],
        ["TC001", "normal", "credit", "normal", "success"],
        ["TC002", "normal", "cash", "normal", "success"],
        ["TC003", "normal", "cash", "restricted", "forbidden"],
        ["TC004", "premium", "cash", "restricted", "failed"],
        ["TC005", "blacklisted", "credit", "normal", "blocked"],
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
