# C# クラスライブラリ + MSTest + テストマトリクス生成ツール

このリポジトリは、`PurchaseService` を題材に以下フローを実現するサンプルです（レポート工程は除外）。

- Excelでテストマトリクスをレビュー
- JSON中間ファイルに変換して管理
- Gherkinを自動生成
- AIへMSTest生成依頼を作成
- AI応答からMSTestコードを取り込み
- `dotnet test` で実行

## C#本体

- ライブラリ: `src/PurchaseLibrary/Class1.cs`
- テスト: `src/PurchaseLibrary.Tests/`

## ツールスクリプト

- `scripts/create_sample_excel.py` サンプルExcel作成
- `scripts/excel_to_json.py` Excel -> JSON
- `scripts/validate_matrix_json.py` JSON検証
- `scripts/generate_gherkin.py` JSON -> Gherkin
- `scripts/build_ai_request.py` AI依頼文生成（MSTest向け）
- `scripts/materialize_ai_tests.py` AI応答 -> `.cs` テストファイル
- `scripts/json_to_excel.py` JSON -> Excel 逆変換

## セットアップ

```bash
python3 -m pip install -r requirements.txt
```

## 一連実行

```bash
make demo
```

`make demo` の実行内容:

1. サンプルExcel生成
2. Excel -> JSON
3. JSONバリデーション
4. Gherkin生成
5. AI依頼ファイル生成
6. AI応答MarkdownからMSTestコード抽出
7. `dotnet test`

## 実AIを使う場合

1. `make ai-request` を実行
2. `artifacts/ai_test_request.md` をAIへ渡す
3. AI回答を `artifacts/<name>.md` として保存
4. 次を実行

```bash
python3 scripts/materialize_ai_tests.py \
  --input artifacts/<name>.md \
  --output src/PurchaseLibrary.Tests/Generated/PurchaseServiceMatrixAiTests.cs

dotnet test MatrixDrivenSample.sln
```

## 補足

- 以前のPythonサンプル一式は `legacy_python_sample/` に退避しています。
