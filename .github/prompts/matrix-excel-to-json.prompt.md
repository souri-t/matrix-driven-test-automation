---
agent: agent
model: GPT-5.3-Codex
description: 因子と水準/テストケースExcelをJSONへ変換する
---

このリポジトリのスキルを使って、ExcelワークブックをJSONに変換してください。

要件:
- スクリプトは `python3 .github/skills/workbook-json-excel-interop/scripts/workbook_excel_to_json.py` を使う
- 入力は `testcases/ticketrequest_pairwise_testcases.xlsx`
- 出力は `testcases/workbook_payload.json`
- 出力JSONは `sheets` 配列を持つ形式にする
- 生成結果（シート数と総行数）を簡潔に報告する
