from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


AGENT_PATH = (
    Path(__file__).resolve().parents[1]
    / "agents"
    / "design-spec-test-matrix.toml"
)


class DesignSpecTestMatrixAgentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agent = tomllib.loads(AGENT_PATH.read_text(encoding="utf-8"))
        cls.instructions = cls.agent["developer_instructions"]

    def test_agent_metadata(self) -> None:
        self.assertEqual(self.agent["name"], "design-spec-test-matrix")
        self.assertIn("仕様書", self.agent["description"])

    def test_gherkin_and_explicit_examples_contract(self) -> None:
        for keyword in ("Feature", "Rule", "Scenario", "Given", "When", "Then"):
            self.assertIn(keyword, self.instructions)
        self.assertIn("明記された判定表、例示、列挙された組み合わせは削減せず", self.instructions)
        self.assertIn("Gherkinは推論用の内部表現に限定", self.instructions)

    def test_audit_classifications_and_approval_gate(self) -> None:
        for classification in (
            "網羅済み",
            "不足",
            "期待値競合",
            "仕様が曖昧",
            "指定箇所の対象外",
        ):
            self.assertIn(classification, self.instructions)
        self.assertIn("ユーザーが対象成果物と追記を明示的に承認", self.instructions)
        self.assertIn("監査前に追記を依頼された場合は監査までで停止", self.instructions)

    def test_json_restoration_and_non_chaining_contract(self) -> None:
        self.assertIn("workbook_json_to_excel.py", self.instructions)
        self.assertIn("元JSONは変更しない", self.instructions)
        self.assertIn("convert-test-matrixの自動実行は行わない", self.instructions)


if __name__ == "__main__":
    unittest.main()
