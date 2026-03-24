# テスト設計スキル

このリポジトリには、用途を分けた 2 つの GitHub Copilot Agent Skill があります。

- マトリクス駆動テスト自動化: `.github/skills/matrix-driven-test-automation/SKILL.md`
- ワークブックJSON/Excel相互変換: `.github/skills/workbook-json-excel-interop/SKILL.md`

## 1. matrix-driven-test-automation

スクリプト群:

- `.github/skills/matrix-driven-test-automation/scripts/`

できること:

- テストマトリクス用のサンプルExcel（`.xlsx`）を作成する
- JSON の妥当性を検証する
- 現在のプロジェクト構成（言語・テストフレームワーク）を推測して、AI向けのテスト生成依頼ファイルを作る
- AI回答からテストコードを取り込み、推測した適切な出力先へ反映する
- すでに作成済みのテストコード（DataRowベース）を逆変換してJSONマトリクスを作る

## 2. workbook-json-excel-interop

スクリプト群:

- `.github/skills/workbook-json-excel-interop/scripts/`

できること:

- Excel（複数シート）をワークブックJSONに変換する
- ワークブックJSONからExcelをリストアする
- 「因子と水準」「テストケース」構成のExcelをJSONで受け渡しする

## JSONフォーマット（ワークブック）

`workbook-json-excel-interop` が扱うJSONは次の形式です。

```json
{
	"sheets": [
		{
			"name": "因子と水準",
			"columns": ["因子", "水準1", "水準2", "水準3", "備考"],
			"rows": [
				{
					"因子": "Soup",
					"水準1": "塩",
					"水準2": "醤油",
					"水準3": "味噌",
					"備考": "必須"
				}
			]
		},
		{
			"name": "テストケース",
			"columns": ["ID", "Soup", "NoodleThickness", "NoodleAmount", "expected", "memo"],
			"rows": [
				{
					"ID": "TC-001",
					"Soup": "塩",
					"NoodleThickness": "細麺",
					"NoodleAmount": "普通",
					"expected": "200 OK / 食券1",
					"memo": "pairwise(valid)"
				}
			]
		}
	]
}
```

## 使い方（推奨）

Copilot Agent に次のように依頼します。

- 「テストマトリクスのサンプルExcelを作って」
- 「ワークブックExcelをJSONへ変換して」
- 「ワークブックJSONからExcelをリストアして」
- 「現在のJSONのテストマトリクスからテストコードを作って」
- 「既存のテストコードからテストマトリクスJSONを作って」

## スラッシュコマンド

- `/code-to-testcase`: 指定コードの入出力から因子/水準を抽出し、ペアワイズのテストケースExcelを作成する
- `/matrix-sample-excel`: テストマトリクス用のサンプルExcelを作成する
- `/matrix-excel-to-json`: 因子/テストケースExcelをワークブックJSONへ変換する
- `/workbook-json-to-excel`: ワークブックJSONからExcelをリストアする
- `/matrix-json-to-testcode`: 現在のJSONからAI依頼生成とテストコード反映をまとめて実行する
- `/matrix-reverse-from-testcode`: 既存テストコード（DataRowベース）からテストマトリクスJSONを逆生成する
