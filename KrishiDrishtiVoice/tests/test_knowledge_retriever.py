import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from agriculture_engine import build_guidance, load_knowledge, search


class KnowledgeRetrieverTests(unittest.TestCase):
    def test_symptom_queries_return_records(self):
        questions = ["My tomato leaves are turning yellow.", "My tomato plant is wilting.", "My tomato leaves have brown spots.", "My tomato leaves are curling.", "My tomato plant is drying even though the soil is wet.", "My tomato crop has insects.", "My tomato fruits are damaged."]
        for question in questions:
            with self.subTest(question=question):
                self.assertTrue(search(question))

    def test_irrelevant_question_falls_back(self):
        guidance = build_guidance("What is the capital of France?")
        self.assertIsNone(guidance["crop"])
        self.assertEqual(guidance["sources"], [])
        self.assertIn("could not match", guidance["understanding"])

    def test_unhealthy_without_crop_is_not_tomato_advice(self):
        guidance = build_guidance("My plant is unhealthy.")
        self.assertIsNone(guidance["crop"])
        self.assertEqual(guidance["sources"], [])

    def test_uncertainty_and_followups_are_present(self):
        guidance = build_guidance("My tomato leaves are turning yellow.")
        self.assertIn("not a confirmed diagnosis", guidance["understanding"])
        self.assertGreaterEqual(len(guidance["follow_up_questions"]), 2)
        self.assertGreaterEqual(len(guidance["possible_explanations"]), 2)

    def test_records_have_source_and_review_metadata(self):
        for record in load_knowledge()["entries"]:
            with self.subTest(record=record["id"]):
                self.assertTrue(record["source"]["url"].startswith("https://"))
                self.assertTrue(record["reviewed_on"])
                self.assertTrue(record["evidence_status"])
                self.assertIn("limitations", record)

    def test_json_is_unicode_safe(self):
        raw = Path(__file__).parents[1].joinpath("knowledge.json").read_text(encoding="utf-8")
        self.assertIn("ಟೊಮೆಟೋ", json.loads(raw)["entries"][0]["keywords"])


if __name__ == "__main__":
    unittest.main()
