---
agent: agent
model: GPT-5.3-Codex
description: ワークブックJSONをExcelへリストアする
---

このリポジトリのスキルを使って、ワークブックJSONをExcelに変換してください。

要件:
- スクリプトは `python3 .github/skills/workbook-json-excel-interop/scripts/workbook_json_to_excel.py` を使う
- 入力は `testcases/workbook_payload.json`
- 出力は `testcases/workbook_payload.xlsx`
- 出力Excelに `因子と水準` と `テストケース` が含まれることを確認する
- 生成結果を簡潔に報告する
