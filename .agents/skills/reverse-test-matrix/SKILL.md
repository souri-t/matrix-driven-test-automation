---
name: reverse-test-matrix
description: 既存のMSTest DataRowテストコードを解析し、因子と水準およびテストケースを共通workbook形式JSONへ逆生成する。既存テストをマトリクス化する、または testcases/testcase_*.json として再利用するときに使う。
---

# 既存テストからマトリクスを逆生成する

## 手順

1. 入力するテストコードのファイルまたはディレクトリを特定する。指定がなく候補が複数ある場合はユーザーに確認する。
2. 出力名を `testcases/testcase_<source>_reversed.json` とする。同名候補が複数ある場合は出力パスを確認する。
3. このSkillディレクトリを基準に次を実行する。

```bash
python3 scripts/testcode_to_workbook_json.py --input <test-path> --output <testcases/testcase_name_reversed.json>
```

4. 出力を再読込し、2シート、必須列、一意なID、空でない期待値を確認する。

## 制約

- 対応形式はC# MSTestの、文字列・真偽値・数値・`null`リテラルで構成された `DataRow` とする。
- パラメータ名から `ID`, `expected`, `memo` を正規化し、残りを因子列とする。
- `因子と水準` はテスト行に実在する一意な値だけから構築する。コードから復元できない未使用水準や設計意図は捏造しない。
- 未対応形式、引数数の不一致、重複ID、空の期待値は黙って読み飛ばさずエラーにする。

## 完了報告

入力・出力パス、解析ファイル数、因子数、ケース数、復元上の制約を報告する。
