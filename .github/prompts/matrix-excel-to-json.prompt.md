---
mode: agent
description: ExcelテストマトリクスをJSONへ変換し、必要なら検証する
---

このリポジトリのスキルを使って、ExcelテストマトリクスをJSONに変換してください。

要件:
- スクリプトは `python3 .github/skills/matrix-driven-test-automation/scripts/excel_to_json.py` を使う
- 入力は `testcases/purchase_matrix.xlsx`
- 出力は `testcases/purchase_matrix.json`
- 変換後、必要なら `validate_matrix_json.py` で再確認する
- 生成/検証結果を簡潔に報告する
