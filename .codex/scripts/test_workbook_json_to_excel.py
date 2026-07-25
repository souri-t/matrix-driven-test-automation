from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook


SCRIPT_DIR = Path(__file__).resolve().parent
JSON_TO_EXCEL = SCRIPT_DIR / "workbook_json_to_excel.py"
EXCEL_TO_JSON = SCRIPT_DIR / "workbook_excel_to_json.py"
VALIDATE_JSON = SCRIPT_DIR / "validate_workbook_json.py"


def sample_payload() -> dict[str, object]:
    return {
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
                        "備考": "",
                    },
                    {
                        "因子": "NoodleAmount",
                        "水準1": "普通",
                        "水準2": "大盛り",
                        "水準3": "",
                        "備考": "Unicodeを保持",
                    },
                ],
            },
            {
                "name": "テストケース",
                "columns": ["ID", "Soup", "NoodleAmount", "expected", "memo"],
                "rows": [
                    {
                        "ID": "TC-001",
                        "Soup": "塩",
                        "NoodleAmount": "普通",
                        "expected": "食券1",
                        "memo": "仕様: Spec/APIプロジェクト概要.md#2.5",
                    },
                    {
                        "ID": "TC-002",
                        "Soup": "味噌",
                        "NoodleAmount": "大盛り",
                        "expected": "要確認",
                        "memo": "",
                    },
                ],
            },
        ]
    }


class WorkbookJsonToExcelTests(unittest.TestCase):
    def test_round_trip_preserves_workbook_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            testcases = Path(temporary) / "testcases"
            testcases.mkdir()
            source = testcases / "testcase_unicode.json"
            source_payload = sample_payload()
            source_text = json.dumps(source_payload, ensure_ascii=False, indent=2)
            source.write_text(source_text, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(JSON_TO_EXCEL), "--input", str(source)],
                check=True,
                capture_output=True,
                text=True,
            )

            workbook_path = source.with_suffix(".xlsx")
            self.assertTrue(workbook_path.is_file())
            self.assertIn("因子と水準=2", result.stdout)
            self.assertEqual(source.read_text(encoding="utf-8"), source_text)

            workbook = load_workbook(workbook_path, data_only=False)
            self.assertEqual(workbook.sheetnames, ["因子と水準", "テストケース"])
            self.assertEqual(workbook["テストケース"]["E2"].value, "仕様: Spec/APIプロジェクト概要.md#2.5")
            self.assertIsNone(workbook["テストケース"]["E3"].value)

            round_trip = testcases / "testcase_roundtrip.json"
            subprocess.run(
                [
                    sys.executable,
                    str(EXCEL_TO_JSON),
                    "--input",
                    str(workbook_path),
                    "--output",
                    str(round_trip),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                json.loads(round_trip.read_text(encoding="utf-8")), source_payload
            )

    def test_existing_workbook_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            testcases = Path(temporary) / "testcases"
            testcases.mkdir()
            source = testcases / "testcase_existing.json"
            source.write_text(
                json.dumps(sample_payload(), ensure_ascii=False), encoding="utf-8"
            )
            workbook_path = source.with_suffix(".xlsx")
            sentinel = b"existing workbook"
            workbook_path.write_bytes(sentinel)

            result = subprocess.run(
                [sys.executable, str(JSON_TO_EXCEL), "--input", str(source)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already exists", result.stderr)
            self.assertEqual(workbook_path.read_bytes(), sentinel)

    def test_invalid_workbook_json_does_not_leave_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            testcases = Path(temporary) / "testcases"
            testcases.mkdir()
            source = testcases / "testcase_invalid.json"
            source.write_text(
                json.dumps({"sheets": []}, ensure_ascii=False), encoding="utf-8"
            )

            result = subprocess.run(
                [sys.executable, str(JSON_TO_EXCEL), "--input", str(source)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing required sheets", result.stderr)
            self.assertFalse(source.with_suffix(".xlsx").exists())

    def test_unresolved_expected_can_be_restored_but_not_implemented(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            testcases = Path(temporary) / "testcases"
            testcases.mkdir()
            source = testcases / "testcase_unresolved.json"
            source.write_text(
                json.dumps(sample_payload(), ensure_ascii=False), encoding="utf-8"
            )

            conversion = subprocess.run(
                [sys.executable, str(JSON_TO_EXCEL), "--input", str(source)],
                check=False,
                capture_output=True,
                text=True,
            )
            validation = subprocess.run(
                [sys.executable, str(VALIDATE_JSON), "--input", str(source)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(conversion.returncode, 0)
            self.assertTrue(source.with_suffix(".xlsx").is_file())
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("Unresolved expected values: TC-002", validation.stderr)


if __name__ == "__main__":
    unittest.main()
