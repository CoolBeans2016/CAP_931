import unittest
from cap_931.report import REPORT_INSTRUCTIONS

from cap_931.report import (
    assemble_report,
    build_report_input,
)


SOURCE = {
    "id": "S1",
    "type": "prospect",
    "title": "Example company",
    "url": "https://example.com",
    "text": "The company builds logistics software.",
}

class ReportTests(unittest.TestCase):
    def test_report_input_keeps_product_context_and_sources_separate(self) -> None:
        report_input = build_report_input(
            product_name="Route Planner",
            prospect_url="https://example.com",
            product_category="Software",
            value_proposition="Reduce planning time",
            target_customer="Logistics teams",
            sources=[SOURCE],
        )

        self.assertIn('"product_context"', report_input)
        self.assertIn('"prospect_url": "https://example.com"', report_input)
        self.assertIn('"id": "S1"', report_input)
        self.assertIn("The company builds logistics software.", report_input)

    def test_report_appends_verified_source_links(self) -> None:
        report = assemble_report("The company builds logistics software [S1].", [SOURCE])

        self.assertIn("## Sources", report)
        self.assertIn("[S1] [Example company](https://example.com)", report)

    def test_report_rejects_unknown_source_ids(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "unknown source IDs: S2"):
            assemble_report("The company has 500 employees [S2].", [SOURCE])

    def test_report_rejects_missing_citations(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "did not cite"):
            assemble_report("The company builds logistics software.", [SOURCE])

    def test_prompt_labels_hypotheses(self) -> None:
        normalized = " ".join(REPORT_INSTRUCTIONS.split())
        self.assertIn(
            "Clearly label evidence-backed observations separately from fit hypotheses and recommendations.",
            normalized,
        )


if __name__ == "__main__":
    unittest.main()
