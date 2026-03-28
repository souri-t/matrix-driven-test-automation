from itertools import combinations, product
from pathlib import Path

from openpyxl import Workbook


factors = {
    "Soup": ["塩", "醤油", "味噌"],
    "NoodleThickness": ["細麺", "太麺"],
    "NoodleAmount": ["普通", "大盛り"],
}

names = list(factors.keys())
all_valid_cases = [dict(zip(names, values)) for values in product(*(factors[n] for n in names))]

uncovered_pairs = set()
for i, j in combinations(range(len(names)), 2):
    for vi in factors[names[i]]:
        for vj in factors[names[j]]:
            uncovered_pairs.add((i, vi, j, vj))


def pairs_in_case(case: dict[str, str]) -> set[tuple[int, str, int, str]]:
    return {
        (i, case[names[i]], j, case[names[j]])
        for i, j in combinations(range(len(names)), 2)
    }


selected = []
remaining = all_valid_cases.copy()
while uncovered_pairs:
    best_case = None
    best_cover = set()
    for case in remaining:
        cover = pairs_in_case(case) & uncovered_pairs
        if len(cover) > len(best_cover):
            best_case = case
            best_cover = cover

    if best_case is None:
        break

    selected.append(best_case)
    uncovered_pairs -= best_cover
    remaining.remove(best_case)

soup_order = {v: i for i, v in enumerate(factors["Soup"])}
thickness_order = {v: i for i, v in enumerate(factors["NoodleThickness"])}
amount_order = {v: i for i, v in enumerate(factors["NoodleAmount"])}

selected.sort(
    key=lambda case: (
        soup_order[case["Soup"]],
        thickness_order[case["NoodleThickness"]],
        amount_order[case["NoodleAmount"]],
    )
)


def ticket_expected(case: dict[str, str]) -> str:
    soup_i = soup_order[case["Soup"]]
    thick_i = thickness_order[case["NoodleThickness"]]
    amount_i = amount_order[case["NoodleAmount"]]
    no = soup_i * 4 + thick_i * 2 + amount_i + 1
    return f"200 OK / 食券{no}"


rows = []
for index, case in enumerate(selected, start=1):
    rows.append(
        {
            "ID": f"TC-{index:03d}",
            "Soup": case["Soup"],
            "NoodleThickness": case["NoodleThickness"],
            "NoodleAmount": case["NoodleAmount"],
            "expected": ticket_expected(case),
            "memo": "pairwise(valid)",
        }
    )

rows.append(
    {
        "ID": "TC-N01",
        "Soup": "",
        "NoodleThickness": "細麺",
        "NoodleAmount": "普通",
        "expected": "400 BadRequest / soup, noodleThickness, noodleAmount are required.",
        "memo": "negative(required check in TicketsController)",
    }
)
rows.append(
    {
        "ID": "TC-N02",
        "Soup": "とんこつ",
        "NoodleThickness": "細麺",
        "NoodleAmount": "普通",
        "expected": "404 NotFound / No matrix entry matched the combination.",
        "memo": "negative(no match in TicketService)",
    }
)

output = Path("/Users/hiyoshiyousuke/Develop/Project/GherkinProject/testcases/ticketrequest_pairwise_testcases.xlsx")
output.parent.mkdir(parents=True, exist_ok=True)

wb = Workbook()
ws_f = wb.active
ws_f.title = "因子と水準"
ws_f.append(["因子", "水準1", "水準2", "水準3", "備考"])
ws_f.append(["Soup", "塩", "醤油", "味噌", "必須。その他値は404想定"])
ws_f.append(["NoodleThickness", "細麺", "太麺", "", "必須"])
ws_f.append(["NoodleAmount", "普通", "大盛り", "", "必須"])
ws_f.append(["expected(出力)", "200 OK / 食券1〜食券12", "400 BadRequest", "404 NotFound", "Controller + Service の推測値"])

ws_t = wb.create_sheet("テストケース")
ws_t.append(["ID", "Soup", "NoodleThickness", "NoodleAmount", "expected", "memo"])
for r in rows:
    ws_t.append([r["ID"], r["Soup"], r["NoodleThickness"], r["NoodleAmount"], r["expected"], r["memo"]])

for col, width in {"A": 12, "B": 14, "C": 18, "D": 14, "E": 62, "F": 46}.items():
    ws_t.column_dimensions[col].width = width
for col, width in {"A": 20, "B": 28, "C": 28, "D": 24, "E": 42}.items():
    ws_f.column_dimensions[col].width = width

wb.save(output)
print(f"created: {output}")
print(f"pairwise_valid_cases: {len(selected)}")
print(f"total_cases: {len(rows)}")
