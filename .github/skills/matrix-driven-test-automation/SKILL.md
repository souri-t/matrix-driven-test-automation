---
name: matrix-driven-test-automation
description: このリポジトリ向けのテストマトリクス駆動ワークフローを実行するスキル。ExcelマトリクスのJSON変換（検証付き）、JSON検証、Gherkin生成、プロジェクト構成から推測したテストフレームワーク向けAI依頼ファイル作成、AI応答からのテストコード反映に使用する。
---

このスキルは、リポジトリで利用するテストマトリクス駆動フロー用のスクリプト群を提供します。
マトリクスは軽量スキーマで、`ID`、`expected`、`memo` を必須列とし、それ以外の列はケースごとに可変です。

## 対応範囲

- Excel（`.xlsx`）でのマトリクス作成・レビュー支援
- Excel -> JSON 変換（中間データ化、検証込み）
- JSON検証（既存JSONの再確認）
- JSON -> Gherkin 生成
- プロジェクト構成から推測したテストフレームワーク向けAI依頼ファイル作成
- AI応答からテストファイルへの反映（言語・拡張子はプロジェクトに合わせて推測）

## 一括依頼

次の自然文で、生成フローを一度に実行できます。

- 「現在のJSONのテストマトリクスからテストコードを作って」

想定される一括実行内容:

1. 現在のJSONからGherkinを生成
2. AI依頼ファイル（artifacts）を生成
3. AI応答Markdownからテストコードを反映

## スクリプト配置

スクリプトはすべて次に配置されています。

- `.github/skills/matrix-driven-test-automation/scripts/`

## 実行コマンド

リポジトリルートで実行してください。

```bash
python3 .github/skills/matrix-driven-test-automation/scripts/create_sample_excel.py --output testcases/purchase_matrix.xlsx
python3 .github/skills/matrix-driven-test-automation/scripts/excel_to_json.py --input testcases/purchase_matrix.xlsx --output testcases/purchase_matrix.json
# 既存JSONの任意再チェック:
python3 .github/skills/matrix-driven-test-automation/scripts/validate_matrix_json.py --input testcases/purchase_matrix.json
python3 .github/skills/matrix-driven-test-automation/scripts/generate_gherkin.py --input testcases/purchase_matrix.json --output features/purchase.feature
python3 .github/skills/matrix-driven-test-automation/scripts/build_ai_request.py --matrix testcases/purchase_matrix.json --output-md artifacts/ai_test_request.md --output-json artifacts/ai_test_bundle.json
python3 .github/skills/matrix-driven-test-automation/scripts/materialize_ai_tests.py --input artifacts/sample_ai_response.md
```

## 依存関係

- Python依存定義: `.github/skills/matrix-driven-test-automation/requirements.txt`

## 注意事項

- マトリクススキーマ定義は `matrix_schema.py` を参照。
- `excel_to_json.py` は必須列（`ID`、`expected`、`memo`）不足やID重複を検出すると即時エラーにします。
- `memo` は備考列であり、テストアサーションには使用しません。
- `ID`、`expected`、`memo` 以外は可変な入力列として扱います。
- 言語・テストフレームワーク・出力先は、現在存在するプロジェクト構成から推測して決定します。
- トレーサビリティ確保のため、`id` を安定キーとして扱います。
- 生成テストコードは `src/PurchaseLibrary.Tests/Generated/` 配下に配置します。
