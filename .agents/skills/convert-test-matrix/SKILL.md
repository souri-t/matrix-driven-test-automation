---
name: convert-test-matrix
description: "`因子と水準` と `テストケース` の2シートを持つテストケースExcelを、同じ内容のworkbook形式JSONへ決定的に変換する。testcases/testcase_*.xlsx をJSON化するときに使う。"
---

# テストマトリクスをJSONへ変換する

## 手順

1. 入力Excelのパスを特定する。指定がなく候補が複数ある場合は、更新日時で選ばずユーザーに確認する。
2. このSkillディレクトリを基準に、次を実行する。

```bash
python3 scripts/workbook_excel_to_json.py --input <xlsx-path>
```

3. スクリプトの検証を通過したことを確認する。入力と同名で拡張子だけを `.json` にしたファイル以外は作成しない。

## 契約

- 入力: `testcases/testcase_*.xlsx`
- 出力: 対応する `testcases/testcase_*.json`
- 必須シート: `因子と水準`, `テストケース`
- `テストケース` の必須列: `ID`, 1列以上の因子列, `expected`, `memo`
- 列順、空セル、Unicode文字列を保持する。

## 完了報告

入力・出力パス、シート数、各シートのデータ行数を報告する。
