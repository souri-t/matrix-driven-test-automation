# Codex運用メモ

このリポジトリは Codex でのテスト設計・テスト実装支援に特化して運用する。

## 構成

- プロンプト定義: `.codex/prompts/*.prompt.md`
- エージェント定義: `.codex/agents/*.agent.md`
- 実行スクリプト: `.codex/prompts/scripts/*.py`

## 標準ワークフロー

1. `code-to-testcase.prompt.md` を使い、対象コードから因子/水準とテストケースExcelを作成する。
2. `matrix-excel-to-json.prompt.md` を使い、Excelをworkbook形式JSONへ変換する。
3. `testcode-writer.agent.md` を使い、JSONを唯一の入力としてテストコードへ反映する。
4. 既存テストコードをマトリクス化する場合は `matrix-reverse-from-testcode.prompt.md` を使う。

## ファイル運用

- テストケースExcel/JSONは `testcases/testcase_*.xlsx` と `testcases/testcase_*.json` を基本形にする。
- 固定名の作業用JSONを前提にしない。
- 一時ファイルを作成した場合は、完了前に削除する。
