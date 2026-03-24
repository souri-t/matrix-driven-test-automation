---
name: workbook-json-excel-interop
description: 因子と水準/テストケースの2シート構成を前提に、ExcelとJSONを相互変換するスキル。
---

このスキルは、次のExcel構成に準拠した相互変換を提供します。

- シート `因子と水準`
- シート `テストケース`

## 対応範囲

- JSON -> Excel 変換（2シート以上の汎用ワークブックにも対応）
- Excel -> JSON 変換（全シートを抽出）
- 因子/テストケースワークブックのAI連携向け中間データ化

## スクリプト配置

- `.github/skills/workbook-json-excel-interop/scripts/`

## 実行コマンド

```bash
python3 .github/skills/workbook-json-excel-interop/scripts/workbook_json_to_excel.py --input testcases/workbook_payload.json --output testcases/workbook_payload.xlsx
python3 .github/skills/workbook-json-excel-interop/scripts/workbook_excel_to_json.py --input testcases/workbook_payload.xlsx --output testcases/workbook_payload.json
```

## JSONフォーマット

ルートは次の形式です。

```json
{
  "sheets": [
    {
      "name": "因子と水準",
      "columns": ["因子", "水準1", "水準2", "水準3", "備考"],
      "rows": [
        {
          "因子": "Soup",
          "水準1": "塩",
          "水準2": "醤油",
          "水準3": "味噌",
          "備考": "必須"
        }
      ]
    },
    {
      "name": "テストケース",
      "columns": ["ID", "Soup", "NoodleThickness", "NoodleAmount", "expected", "memo"],
      "rows": [
        {
          "ID": "TC-001",
          "Soup": "塩",
          "NoodleThickness": "細麺",
          "NoodleAmount": "普通",
          "expected": "200 OK / 食券1",
          "memo": "pairwise(valid)"
        }
      ]
    }
  ]
}
```

## 注意事項

- Excelの先頭行はヘッダーとして扱います。
- 空行は読み取り時にスキップします。
- 出力JSONは `rows` をオブジェクト配列で保持します。
