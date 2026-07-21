# Codex運用メモ

このリポジトリはCodexによるテスト設計・テスト実装支援に特化して運用する。

## Skill

- `design-test-matrix`: 対象コードから因子・水準とテストケースExcelを作成する。
- `convert-test-matrix`: Excelをworkbook形式JSONへ変換する。
- `write-matrix-tests`: 確定済みJSONを唯一のテスト設計入力としてテストコードへ反映する。
- `reverse-test-matrix`: 既存のMSTest DataRowテストをworkbook形式JSONへ逆生成する。

Skillは `.agents/skills/<skill-name>/` に置く。Codex App、CLI、IDEでは自然文または `$skill-name` で工程ごとに利用する。

## 標準ワークフロー

1. `$design-test-matrix` で対象コードから `testcases/testcase_*.xlsx` を作成する。
2. `$convert-test-matrix` でExcelを同名の `testcases/testcase_*.json` へ変換する。
3. `$write-matrix-tests` でJSONの全ケースをテストコードへ反映し、対象テストを実行する。
4. 既存テストをマトリクス化する場合は `$reverse-test-matrix` を単独で使う。

工程は自動連鎖させず、指定されたSkillの責務だけを実行する。テスト実装時に因子・水準の再設計やペアワイズ再計算を行わない。

## ファイル運用

- Excel/JSONは `testcases/testcase_*.xlsx` と `testcases/testcase_*.json` を基本形にする。
- 入力候補が複数あり対象が指定されていない場合は、更新日時で推測せずユーザーに確認する。
- 固定名の作業用JSONを前提にしない。
- 一時ファイルを作成した場合は完了前に削除する。
