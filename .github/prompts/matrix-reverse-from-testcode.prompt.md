---
agent: agent
model: GPT-5.3-Codex
description: 既存テストコードからテストマトリクスJSONを逆生成する
---

既存テストコードを逆変換して、テストマトリクスJSONを作成してください。

要件:
- スクリプトは `python3 .github/skills/matrix-driven-test-automation/scripts/testcode_to_json.py` を使う
- 出力先は `testcases/reversed_matrix.json`
- 生成後、`id / expected / memo` が含まれていることを確認する
- 結果を簡潔に報告する
