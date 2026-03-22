# テストマトリクス変換スキル

このリポジトリには、テストマトリクスを扱うための GitHub Copilot Agent Skill が用意されています。

- スキル定義: `.github/skills/matrix-driven-test-automation/SKILL.md`
- スクリプト群: `.github/skills/matrix-driven-test-automation/scripts/`

## このスキルでできること

- テストマトリクス用のサンプルExcel（`.xlsx`）を作成する
- Excelテストマトリクス（`.xlsx`）を JSON に変換する
- JSON の妥当性を検証する
- 現在のプロジェクト構成（言語・テストフレームワーク）を推測して、AI向けのテスト生成依頼ファイルを作る
- AI回答からテストコードを取り込み、推測した適切な出力先へ反映する
- すでに作成済みのテストコード（DataRowベース）を逆変換してJSONマトリクスを作る

## データ仕様

- 必須列: `ID`, `expected`, `memo`
- `memo` は備考列で、テストの合否判定には使わない
- 上記以外の列は、ケースごとの可変入力列として扱う

## 使い方（推奨）

Copilot Agent に次のように依頼します。

- 「テストマトリクスのサンプルExcelを作って」
- 「テストケースExcelをJSONに変換して」
- 「現在のJSONのテストマトリクスからテストコードを作って」
- 「既存のテストコードからテストマトリクスJSONを作って」

## 既にテストコードを作成済みの場合

既存テストコードから逆変換してJSONを作ることができます。

- 想定: `src/...Tests/...` の DataRow ベースのテストコード
- 出力: `testcases/reversed_matrix.json`（既定）
- 依頼例: 「既存のテストコードからテストマトリクスJSONを作って」

補足:

- 必須列 `id`, `expected`, `memo` を含む形式で出力します。
- `memo` がテストコードにない場合は空文字で補完します。

## 補足

- 既存の生成先ファイルがある場合、テストコード反映時にそのファイルは上書きされます。
- 最終的なテスト実行は、プロジェクトに合わせて通常のテストコマンドで実施してください（例: `dotnet test src/MatrixDrivenSample.sln`）。
