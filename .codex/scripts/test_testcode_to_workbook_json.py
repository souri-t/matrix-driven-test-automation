from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from testcode_to_workbook_json import build_payload


SCRIPT = Path(__file__).resolve().parent / "testcode_to_workbook_json.py"


class TestcodeToWorkbookJsonTests(unittest.TestCase):
    def test_factor_levels_are_reversed_as_one_level_per_row(self) -> None:
        source = """
        [DataRow("TC-001", "塩", "普通", "食券1")]
        [DataRow("TC-002", "醤油", "大盛り", "食券6")]
        [DataRow("TC-003", "塩", "大盛り", "食券2")]
        public void ResolveExpected(
            string id,
            string soup,
            string noodleAmount,
            string expected)
        {
        }
        """
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "TicketServiceTests.cs"
            path.write_text(source, encoding="utf-8")

            payload = build_payload(
                [path],
                {
                    "テスト対象": "TicketService.ResolveExpected",
                    "テストの目的": {
                        "TC-001": "塩・普通盛りの食券を確認する",
                        "TC-002": "醤油・大盛りの食券を確認する",
                        "TC-003": "塩・大盛りの食券を確認する",
                    },
                },
            )

        self.assertEqual(
            [sheet["name"] for sheet in payload["sheets"]],
            ["テスト対象", "因子と水準", "テストケース"],
        )
        target_sheet = payload["sheets"][0]
        self.assertEqual(
            target_sheet["rows"],
            [
                {
                    "テスト対象": "TicketService.ResolveExpected",
                    "根拠資料": path.as_posix(),
                    "参照箇所": "DataRowメソッド: ResolveExpected",
                    "参照目的": "既存テストケースの復元",
                    "備考": "",
                }
            ],
        )
        factor_sheet = payload["sheets"][1]
        self.assertEqual(factor_sheet["name"], "因子と水準")
        self.assertEqual(factor_sheet["columns"], ["因子", "水準", "備考"])
        self.assertEqual(
            factor_sheet["rows"],
            [
                {
                    "因子": "soup",
                    "水準": "塩",
                    "備考": "既存DataRowに現れる値から復元",
                },
                {
                    "因子": "soup",
                    "水準": "醤油",
                    "備考": "既存DataRowに現れる値から復元",
                },
                {
                    "因子": "noodleAmount",
                    "水準": "普通",
                    "備考": "既存DataRowに現れる値から復元",
                },
                {
                    "因子": "noodleAmount",
                    "水準": "大盛り",
                    "備考": "既存DataRowに現れる値から復元",
                },
            ],
        )
        test_sheet = payload["sheets"][2]
        self.assertEqual(
            test_sheet["columns"],
            [
                "ID",
                "テストの目的",
                "soup",
                "noodleAmount",
                "expected",
                "memo",
            ],
        )
        self.assertEqual(
            test_sheet["rows"][0]["テストの目的"],
            "塩・普通盛りの食券を確認する",
        )

    def test_missing_generated_purpose_is_rejected(self) -> None:
        source = """
        [DataRow("TC-001", "塩", "食券1")]
        public void ResolveExpected(string id, string soup, string expected)
        {
        }
        """
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "TicketServiceTests.cs"
            path.write_text(source, encoding="utf-8")

            with self.assertRaisesRegex(
                ValueError,
                "missing テストの目的 for TC-001",
            ):
                build_payload(
                    [path],
                    {
                        "テスト対象": "TicketService.ResolveExpected",
                        "テストの目的": {},
                    },
                )

    def test_existing_purpose_parameter_is_preserved(self) -> None:
        source = """
        [DataRow("TC-001", "塩の結果を確認する", "塩", "食券1")]
        public void ResolveExpected(
            string id,
            string testPurpose,
            string soup,
            string expected)
        {
        }
        """
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "TicketServiceTests.cs"
            path.write_text(source, encoding="utf-8")

            payload = build_payload(
                [path],
                {
                    "テスト対象": "TicketService.ResolveExpected",
                    "テストの目的": {},
                },
            )

        self.assertEqual(
            payload["sheets"][2]["rows"][0]["テストの目的"],
            "塩の結果を確認する",
        )

    def test_cli_uses_enrichment_file_and_writes_three_sheets(self) -> None:
        source = """
        [DataRow("TC-001", "塩", "食券1")]
        public void ResolveExpected(string id, string soup, string expected)
        {
        }
        """
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "TicketServiceTests.cs"
            path.write_text(source, encoding="utf-8")
            enrichment = root / "enrichment.json"
            enrichment.write_text(
                json.dumps(
                    {
                        "テスト対象": "TicketService.ResolveExpected",
                        "テストの目的": {
                            "TC-001": "塩味の食券を確認する",
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            testcases = root / "testcases"
            output = testcases / "testcase_ticket_reversed.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(path),
                    "--output",
                    str(output),
                    "--enrichment",
                    str(enrichment),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("Reversed 1 files / 1 factors / 1 cases", result.stdout)
            self.assertEqual(
                [sheet["name"] for sheet in payload["sheets"]],
                ["テスト対象", "因子と水準", "テストケース"],
            )

    def test_unknown_enrichment_id_is_rejected(self) -> None:
        source = """
        [DataRow("TC-001", "塩", "食券1")]
        public void ResolveExpected(string id, string soup, string expected)
        {
        }
        """
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "TicketServiceTests.cs"
            path.write_text(source, encoding="utf-8")

            with self.assertRaisesRegex(
                ValueError,
                "unknown test case IDs: TC-999",
            ):
                build_payload(
                    [path],
                    {
                        "テスト対象": "TicketService.ResolveExpected",
                        "テストの目的": {
                            "TC-001": "塩味の食券を確認する",
                            "TC-999": "存在しないケース",
                        },
                    },
                )


if __name__ == "__main__":
    unittest.main()
