# Codex運用メモ

このリポジトリはCodexのカスタムエージェントによるテスト設計・テスト実装支援に特化して運用する。

## カスタムエージェント

- `design-test-matrix`: 対象コードから因子・水準とテストケースExcelを作成する。
- `convert-test-matrix`: Excelをworkbook形式JSONへ変換する。
- `testcode-writer`: 確定済みJSONを唯一のテスト設計入力としてテストコードへ反映・検証する。
- `reverse-test-matrix`: 既存のMSTest DataRowテストをworkbook形式JSONへ逆生成する。

エージェント定義は公式のプロジェクト配置である `.codex/agents/*.toml` に置く。各工程ではCodexへ利用するエージェント名と対象パスを明示する。

## 標準ワークフロー

1. `design-test-matrix` に対象コードから `testcases/testcase_*.xlsx` を作成させる。
2. `convert-test-matrix` にExcelを同名の `testcases/testcase_*.json` へ変換させる。
3. `testcode-writer` にJSONの全ケースをテストコードへ反映させ、対象テストを実行させる。
4. 既存テストをマトリクス化する場合は `reverse-test-matrix` を単独で使う。

工程は自動連鎖させず、指定されたエージェントの責務だけを実行する。テスト実装時に因子・水準の再設計やペアワイズ再計算を行わない。

## ファイル運用

- エージェントが使う決定的処理は `.codex/scripts/*.py` に置く。
- Excel/JSONは `testcases/testcase_*.xlsx` と `testcases/testcase_*.json` を基本形にする。
- 入力候補が複数あり対象が未指定の場合は、更新日時で推測せずユーザーに確認する。
- 固定名の作業用JSONを前提にしない。
- 一時ファイルを作成した場合は完了前に削除する。
