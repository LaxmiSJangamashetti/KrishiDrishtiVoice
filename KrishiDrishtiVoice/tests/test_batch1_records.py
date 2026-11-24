import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from agriculture_engine import build_guidance, parse_question, search


class Batch1RecordTests(unittest.TestCase):
    def assert_topic(self, question, symptom, record_id):
        parsed = parse_question(question)
        self.assertEqual(parsed["crop"], "tomato")
        self.assertEqual(parsed["symptom"], symptom)
        matches = search(question)
        self.assertTrue(matches)
        self.assertEqual(matches[0].record["id"], record_id)

    def test_waterlogging_questions(self):
        self.assert_topic("My tomato field has standing water.", "waterlogging", "tomato-waterlogging-001")
        self.assert_topic("My tomato plants are wilting even though the soil is wet.", "waterlogging", "tomato-waterlogging-001")

    def test_water_stress_questions(self):
        self.assert_topic("My tomato plants are wilting and the soil is dry.", "water_stress", "tomato-water-stress-001")
        self.assert_topic("I irrigated my tomato plants yesterday.", "water_stress", "tomato-water-stress-001")

    def test_whitefly_is_observation_only(self):
        self.assert_topic("There are tiny white insects under my tomato leaves.", "whitefly_observation", "tomato-whitefly-001")
        parsed = parse_question("My tomato leaves are yellow but I cannot see insects.")
        self.assertEqual(parsed["symptom"], "leaf_yellowing")
        self.assertNotEqual(search("My tomato leaves are yellow but I cannot see insects.")[0].record["id"], "tomato-whitefly-001")

    def test_fruit_borer_observation(self):
        self.assert_topic("My tomato fruit has entry holes and frass.", "fruit_borer_observation", "tomato-fruit-borer-001")
        guidance = build_guidance("My tomato fruit has entry holes and frass.")
        self.assertIn("not a confirmed diagnosis", guidance["uncertainty"])

    def test_leaf_miner_observation(self):
        self.assert_topic("There are winding serpentine trails inside my tomato leaves.", "leaf_miner_observation", "tomato-leaf-miner-001")

    def test_batch1_records_do_not_offer_chemical_control(self):
        for question in [
            "My tomato field has standing water.",
            "There are tiny white insects under my tomato leaves.",
            "My tomato fruit has entry holes and frass.",
            "There are winding serpentine trails inside my tomato leaves.",
        ]:
            with self.subTest(question=question):
                answer = build_guidance(question)["safe_actions"]
                self.assertFalse(any("apply a dose" in action.lower() or "apply chemical" in action.lower() for action in answer))


if __name__ == "__main__":
    unittest.main()
