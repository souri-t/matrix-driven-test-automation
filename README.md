# C# クラスライブラリ + MSTest + テストマトリクス駆動開発

このリポジトリは `PurchaseService` を題材に、以下フローを実現するサンプルです（レポート工程は除外）。

- Excelでテストマトリクスをレビュー
- JSON中間ファイルに変換して管理
- Gherkinを自動生成
- AIへMSTest生成依頼を作成
- AI応答からMSTestコードを取り込み
- `dotnet test` で実行

## C#本体

- ライブラリ: `src/PurchaseLibrary/Class1.cs`
- テスト: `src/PurchaseLibrary.Tests/`

## Agent Skill

このリポジトリでは、ツール処理は GitHub Copilot Agent Skill として管理します。

- Skill定義: `.github/skills/matrix-driven-test-automation/SKILL.md`
- 実装リソース: `.github/skills/matrix-driven-test-automation/`

方針:

- 通常運用ではスクリプトを直接実行しない
- Copilot Agent に依頼して Skill を呼び出す

## 依頼例（Copilot Agent向け）

- 「テストケースExcelをJSONに変換して、バリデーションまで実行して」
- 「現在のJSONからGherkinを再生成して」
- 「このJSONを使ってMSTest生成用のAI依頼ファイルを作って」
- 「AI回答MarkdownからMSTestコードを取り込んで、`dotnet test` を実行して」

## 生成物の配置

- テストケース: `testcases/`
- Gherkin: `features/`
- AI入出力: `artifacts/`
- 生成テストコード: `src/PurchaseLibrary.Tests/Generated/`

## 補足

- `dotnet test MatrixDrivenSample.sln` は通常どおり実行可能です。
