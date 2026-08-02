from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


AGENT_DIR = Path(__file__).resolve().parents[1] / "agents"
AGENT_NAMES = (
    "design-test-matrix",
    "design-spec-test-matrix",
    "convert-test-matrix",
    "testcode-writer",
    "reverse-test-matrix",
)


class AgentDataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.instructions = {
            name: tomllib.loads(
                (AGENT_DIR / f"{name}.toml").read_text(encoding="utf-8")
            )["developer_instructions"]
            for name in AGENT_NAMES
        }

    def test_all_agents_use_three_sheet_contract(self) -> None:
        for name, instructions in self.instructions.items():
            with self.subTest(agent=name):
                for sheet in ("テスト対象", "因子と水準", "テストケース"):
                    self.assertIn(sheet, instructions)
                self.assertIn("テストの目的", instructions)

    def test_design_agents_do_not_persist_coverage_state(self) -> None:
        for name in ("design-test-matrix", "design-spec-test-matrix"):
            with self.subTest(agent=name):
                instructions = self.instructions[name]
                self.assertIn("網羅性", instructions)
                self.assertIn("Excelへ追加しない", instructions)

    def test_reverse_agent_requires_ai_enrichment_and_cleanup(self) -> None:
        instructions = self.instructions["reverse-test-matrix"]
        self.assertIn("--enrichment", instructions)
        self.assertIn("実際の対象クラス・メソッド", instructions)
        self.assertIn("一時JSONと一時ディレクトリを削除", instructions)

    def test_testcode_writer_still_blocks_unresolved_expected(self) -> None:
        instructions = self.instructions["testcode-writer"]
        self.assertIn('expectedが「要確認」', instructions)
        self.assertIn("実装を停止", instructions)


if __name__ == "__main__":
    unittest.main()
