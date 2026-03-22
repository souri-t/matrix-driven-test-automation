---
mode: agent
description: 現在のJSONテストマトリクスからテストコードを反映する
---

現在のJSONテストマトリクスから、プロジェクト構成を推測してテストコードを反映してください。

要件:
- `build_ai_request.py` でAI依頼ファイルを生成する
- AI応答Markdownが `artifacts/sample_ai_response.md` にある前提で `materialize_ai_tests.py` を実行する
- 既存の生成先ファイルがある場合、上書きされることを明示する
- 実行したファイルパスと結果を報告する
