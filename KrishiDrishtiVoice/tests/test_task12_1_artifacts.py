import json
import unittest
from pathlib import Path

from agriculture_engine import load_knowledge


class Task121ArtifactTests(unittest.TestCase):
    def test_rice_records_have_sources_and_no_dosage_actions(self):
        records = [r for r in load_knowledge()["entries"] if r["crop"] == "rice"]
        self.assertGreaterEqual(len(records), 2)
        for record in records:
            self.assertTrue(record["source"]["url"].startswith("https://"))
            self.assertTrue(record["limitations"])
            self.assertFalse(any("g/l" in action or "kg/ha" in action for action in record["safe_initial_actions"]))

    def test_model_mapping_covers_all_ten_classes_conservatively(self):
        path = Path(__file__).parents[1] / "MODEL_KNOWLEDGE_MAPPING.json"
        mapping = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["classes"]), 10)
        self.assertTrue(all(item["guidance_eligible"] is False for item in mapping["classes"]))

    def test_source_register_keeps_tomato_website_reference_only(self):
        path = Path(__file__).parents[1] / "AGRICULTURAL_SOURCE_REGISTER.json"
        register = json.loads(path.read_text(encoding="utf-8"))
        tomato = [item for item in register["sources"] if "tomato-crop.web.app" in item["url"]]
        self.assertTrue(tomato)
        self.assertTrue(all("pending" in item["status"] or "not imported" in item["status"] or "reference" in item["status"] or "pest_categories_only" in item["status"] for item in tomato))


if __name__ == "__main__":
    unittest.main()
