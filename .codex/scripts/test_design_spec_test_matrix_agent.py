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

    def test_text_fallback_and_parent_handoff_contract(self) -> None:
        for text in (
            "USER_DECISION_REQUIRED",
            "理由: <停止理由>",
            "変更: 未実施",
            "回答方法:",
            "選択UIを利用できない場合",
            "呼び出し元エージェントへ返す",
        ):
            self.assertIn(text, self.instructions)
        self.assertIn(
            "ユーザー回答前にExcel、JSON、その他の成果物を変更しない",
            self.instructions,
        )

    def test_specification_mismatch_gate_and_exclusions(self) -> None:
        for trigger in (
            "同じ前提と入力",
            "期待値が明確に異なる",
            "対象機能、主要因子、操作が既存ケースと対応せず",
        ):
            self.assertIn(trigger, self.instructions)
        for exclusion in (
            "単なる不足ケース",
            "既存側だけの追加ケース",
            "用語・表記の違いだけ",
        ):
            self.assertIn(exclusion, self.instructions)
        self.assertIn(
            "「仕様指定の要確認」は他の監査分類やExcel生成確認より先",
            self.instructions,
        )
        self.assertIn(
            "競合する既存期待値は変更せず",
            self.instructions,
        )

    def test_artifact_specific_decision_options(self) -> None:
        for state in (
            "Excelが存在する場合",
            "JSONだけが存在し、同名Excelが存在しない場合",
            "ExcelもJSONも存在しない場合",
        ):
            self.assertIn(state, self.instructions)
        self.assertIn("GAP-001から始まる一意な選択用ID", self.instructions)
        self.assertIn("指定したGAP ID", self.instructions)
        self.assertIn("正式なTC IDとは区別", self.instructions)
        self.assertIn(
            "最初から新規Excel作成を明示した依頼では、Excel生成可否を重ねて質問せず",
            self.instructions,
        )

    def test_reaudit_before_mutation_contract(self) -> None:
        self.assertIn(
            "ユーザー回答後、追記またはExcel生成の直前に仕様と対象成果物を再読込",
            self.instructions,
        )
        self.assertIn(
            "内容が変化していた場合は変更せず",
            self.instructions,
        )

    def test_json_restoration_and_non_chaining_contract(self) -> None:
        self.assertIn("workbook_json_to_excel.py", self.instructions)
        self.assertIn("元JSONは変更しない", self.instructions)
        self.assertIn("convert-test-matrixの自動実行は行わない", self.instructions)


if __name__ == "__main__":
    unittest.main()
