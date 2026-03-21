# テストケース作成ツール

## 概要

本ドキュメントは、以下の開発フローを実現するための仕組み設計をまとめたものである。

```
[ Excel（マトリクス編集・レビュー） ]
            ↓（エクスポート）
[ JSON（中間データ・Git管理） ]
            ↓（生成）
[ Gherkin（Scenario Outline） ]
            ↓
[ テストコード / 実行 ]
            ↓
[ レポート ]
```

---

## 全体方針

### 基本原則

* Excelは「ビュー専用」とする（Git管理しない）
* JSONを唯一の真実（Single Source of Truth）とする
* Gherkinは生成物とする（手書き禁止）
* テストコードもGherkinに従属させる

### 想定

* テストパターンはExcelで人間が作る場合もあるが、AIがJSONを直接生成するケースも想定する。
* Excelはあくまで人間のためのUIであり、JSONが機械処理のためのデータフォーマットである。
* AIが作成したテストパターンのJSONからExcelへの逆変換は行えるようにする。

---

## 必要な全工程

1. テストケースExcelをJSONに変換する
2. Gherkin生成する
3. AI依頼ファイルを生成する
4. テストコードへ反映する

## 各工程の依頼例（Copilot Agent向け）

1. テストケースExcelをJSONに変換する
「テストケースExcelをJSONに変換して」

2. Gherkin生成する
「現在のJSONからGherkinを生成して」

3. AI依頼ファイルを生成する
「このJSONを使ってMSTest生成用のAI依頼ファイルを作って」

4. テストコードへ反映する
「AI回答MarkdownからMSTestコードを取り込み、テストプロジェクトへ反映して」

## 生成物の配置

- テストケース: `testcases/`
- Gherkin: `features/`
- AI入出力: `artifacts/`
- 生成テストコード: `src/PurchaseLibrary.Tests/Generated/`

## 補足

- マトリクスは `ID`、`expected`、`memo` を必須列とし、それ以外の列はテストケースごとに可変です。
- `memo` は備考欄で、テスト結果判定には使用しません。
- JSONバリデーションは `excel_to_json` 実行時に自動で行われます（必須列、ID重複チェック）。
- 既存JSONのみを再確認したい場合は、`validate_matrix_json` を補助的に利用できます。
- 最終確認は `dotnet test src/MatrixDrivenSample.sln` で実行可能です。
