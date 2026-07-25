# テスト設計ツール

コードまたは仕様書からテストケースを設計し、Excel・JSON・テストコードへ段階的に反映するCodex向けカスタムエージェント集です。各プロジェクトへ `.codex/` を手動配置して利用します。

## 配置

このリポジトリの `.codex` フォルダを対象プロジェクトのルートへコピーします。

```text
target-project/
├── .codex/
│   ├── agents/
│   │   ├── design-test-matrix.toml
│   │   ├── design-spec-test-matrix.toml
│   │   ├── convert-test-matrix.toml
│   │   ├── testcode-writer.toml
│   │   └── reverse-test-matrix.toml
│   └── scripts/
│       ├── workbook_excel_to_json.py
│       ├── workbook_json_to_excel.py
│       ├── validate_workbook_json.py
│       ├── testcode_to_workbook_json.py
│       └── requirements.txt
└── AGENTS.md
```

Excel変換にはPythonと `openpyxl` が必要です。

```bash
python3 -m pip install -r .codex/scripts/requirements.txt
```

対象プロジェクトに既存の `.codex` がある場合は、フォルダ全体を上書きせず `agents/` と `scripts/` の内容をマージしてください。`AGENTS.md` の運用ルールも必要に応じて対象プロジェクトへ追記します。

## エージェント一覧

| エージェント | 入力 | 出力 |
| --- | --- | --- |
| `design-test-matrix` | コードまたはフォルダ | `testcases/testcase_*.xlsx` |
| `design-spec-test-matrix` | 仕様書の指定箇所、任意で既存Excel/JSON | 新規または追記した `.xlsx`、もしくは読取専用の監査結果 |
| `convert-test-matrix` | `testcases/testcase_*.xlsx` | 同名の `.json` |
| `testcode-writer` | `testcases/testcase_*.json` | テストコード |
| `reverse-test-matrix` | MSTest DataRowコード | `testcases/testcase_*_reversed.json` |

## 基本ワークフロー

各工程は独立しており、自動では連鎖しません。Codexへエージェント名と対象パスを明示します。

```text
design-test-matrix エージェントに src/TicketService.cs のテストケースExcelを作成させてください。
```

```text
convert-test-matrix エージェントに testcases/testcase_ticketservice_resolveexpected.xlsx をJSONへ変換させてください。
```

```text
testcode-writer エージェントに testcases/testcase_ticketservice_resolveexpected.json からテストを実装させてください。
```

既存テストをマトリクス化する場合は次のように依頼します。

```text
reverse-test-matrix エージェントに src/Example.Tests/TicketServiceTests.cs をJSONへ逆生成させてください。
```

## 仕様書起点のワークフロー

仕様書起点では、ファイルだけでなく対象の見出し・ページ・行範囲なども指定します。エージェントは対象箇所を内部的にGherkinへ整理しますが、`.feature` は保存しません。仕様に明記された判定表や具体例は削減せず、Excelの各ケースへ対応させます。

新規にExcelを作成する例:

```text
design-spec-test-matrix エージェントに Spec/APIプロジェクト概要.md の
「2. アプリ機能仕様（TicketService）」からテストケースExcelを作成させてください。
```

既存成果物を監査する例:

```text
design-spec-test-matrix エージェントに Spec/APIプロジェクト概要.md の
「2. アプリ機能仕様（TicketService）」を根拠として、
testcases/testcase_ticketservice_resolveexpected.xlsx の網羅性を監査させてください。
```

監査は成果物を変更せず、各仕様シナリオを「網羅済み」「不足」「期待値競合」「仕様が曖昧」に分類し、既存ケースのうち指定箇所では判断できないものを「指定箇所の対象外」として報告します。不足ケースを追記する場合は、監査結果を確認してから対象と追記を明示します。

```text
直前の監査で不足とされたケースを、
testcases/testcase_ticketservice_resolveexpected.xlsx へ追記してください。
```

新しい因子列が必要な場合、エージェントはExcelを変更せず、必要な構造変更を提案します。期待結果を仕様から確定できないケースは `expected` を `要確認` として残すため、解決するまで `testcode-writer` は実装を開始しません。

監査対象がJSONだけの場合、監査はJSONを直接読みます。追記が承認されると次のスクリプトで同名Excelを復元し、そのExcelへ不足ケースを追加します。元JSONは変更されません。

```bash
python3 .codex/scripts/workbook_json_to_excel.py \
  --input testcases/testcase_ticketservice_resolveexpected.json
```

追記後のJSONが必要な場合は、`convert-test-matrix` を別工程として実行します。監査、追記、JSON再生成は自動連鎖しません。

```mermaid
flowchart TD
    A(["対象コード"]) --> B["design-test-matrix"]
    B --> C(["testcases/testcase_&lt;class&gt;_&lt;method&gt;.xlsx"])
    C --> D["convert-test-matrix"]
    D --> E(["testcases/testcase_&lt;class&gt;_&lt;method&gt;.json"])
    E --> F["testcode-writer"]
    F --> G(["既存形式に沿ったテストコード"])

    H(["既存MSTest DataRowテスト"]) --> I["reverse-test-matrix"]
    I --> J(["testcases/testcase_&lt;source&gt;_reversed.json"])

    K(["仕様書の指定箇所"]) --> L["design-spec-test-matrix"]
    L --> M(["新規Excel"])
    L --> N(["既存Excel/JSONの監査結果"])
    N --> O{"ユーザーが追記を承認"}
    O -->|Excel| P(["既存Excelへ追記"])
    O -->|JSONのみ| Q["同名Excelへ復元して追記"]
```

## データ契約

ExcelとJSONは次の2シートを持ちます。

- `因子と水準`
- `テストケース`

`テストケース` の列は `ID`、1列以上の因子列、`expected`、`memo` です。JSONは同じ内容をworkbook形式の `sheets` 配列で表現します。

仕様起点のケースでは、`memo` に仕様書パス、対象箇所、内部シナリオ名を記録して根拠を追跡できるようにします。既存のシート構成や列契約は変更しません。

逆生成では、既存DataRowに実際に現れる値だけから `因子と水準` を復元します。元のテストコードから判定できない未使用水準や設計意図は補完しません。

## 開発時の検証

変換スクリプトのテストは次で実行できます。

```bash
python3 -m unittest discover -s .codex/scripts -p 'test_*.py' -v
```
