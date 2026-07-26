from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from testcode_to_workbook_json import build_payload


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

            payload = build_payload([path])

        factor_sheet = payload["sheets"][0]
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


if __name__ == "__main__":
    unittest.main()
