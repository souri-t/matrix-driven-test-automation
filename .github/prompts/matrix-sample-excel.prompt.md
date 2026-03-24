---
agent: agent
model: GPT-5.3-Codex
description: 新仕様（workbook payload）に準拠したサンプルExcelを作成する
---

このリポジトリのスキルを使って、新仕様のサンプルExcelを作成してください。

要件:
- 入力JSONは `testcases/workbook_payload.sample.json` を使う
- スクリプトは `python3 .github/skills/workbook-json-excel-interop/scripts/workbook_json_to_excel.py` を使う
- 出力先は `testcases/workbook_payload.sample.xlsx`
- 出力Excelに `因子と水準` と `テストケース` が含まれることを確認する
- 実行後、作成結果のファイルパスを報告する
