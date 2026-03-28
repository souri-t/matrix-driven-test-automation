---
agent: agent
model: GPT-5.3-Codex
description: テスト作成依頼ファイル群をもとに testcode-writer へ委譲してテストコードを反映する
---

このプロンプトは、テストコード作成専用エージェント `testcode-writer` へ委譲する入口です。
設計フェーズ（`code-to-testcase` / `matrix-excel-to-json`）の成果物を前提に、実装フェーズのみを実施してください。

要件:
- `testcode-writer` を使って実装フェーズを進める
- 中間成果物 `artifacts/ai_test_request.md` / `artifacts/ai_test_bundle.json` / `artifacts/sample_ai_response.md` を前提入力として扱う
- 既存の生成先ファイルがある場合、上書きされることを明示する
- 生成されたファイルパスと結果を報告する
