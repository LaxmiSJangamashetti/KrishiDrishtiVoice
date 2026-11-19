import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from agriculture_engine import build_guidance, parse_question, search, validate_safety


class KannadaUnderstandingTests(unittest.TestCase):
    def assert_kannada_topic(self, question, symptom, record_id):
        parsed = parse_question(question)
        self.assertEqual(parsed["crop"], "tomato")
        self.assertEqual(parsed["symptom"], symptom)
        matches = search(question)
        self.assertTrue(matches)
        self.assertEqual(matches[0].record["id"], record_id)
        guidance = build_guidance(question, "ಕನ್ನಡ (Kannada)")
        self.assertNotIn("could not match", guidance["understanding"].lower())
        self.assertTrue(guidance["follow_up_questions"])
        self.assertIn("not a confirmed diagnosis", guidance["uncertainty"])

    def test_yellowing_variations(self):
        for question in [
            "ನನ್ನ ಟೊಮೆಟೋ ಗಿಡದ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ.",
            "ಟೊಮಾಟೊ ಎಲೆಗಳು ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿವೆ.",
        ]:
            self.assert_kannada_topic(question, "leaf_yellowing", "tomato-leaf-yellowing-001")

    def test_wilting_variations(self):
        for question in [
            "ನನ್ನ ಟೊಮೆಟೋ ಗಿಡ ಒಣಗುತ್ತಿದೆ.",
            "ಟೊಮೆಟೋ ಗಿಡಗಳು ಬಾಡುತ್ತಿವೆ.",
        ]:
            self.assert_kannada_topic(question, "wilting", "tomato-water-stress-001")

    def test_waterlogging_variations(self):
        for question in [
            "ನನ್ನ ಟೊಮೆಟೋ ಹೊಲದಲ್ಲಿ ನೀರು ನಿಂತಿದೆ.",
            "ನನ್ನ ಟೊಮೆಟೋ ಗಿಡಗಳ ಮಣ್ಣು ತುಂಬಾ ಒದ್ದೆಯಾಗಿದೆ, ಗಿಡಗಳು ಬಾಡುತ್ತಿವೆ.",
        ]:
            self.assert_kannada_topic(question, "waterlogging", "tomato-waterlogging-001")

    def test_water_stress_variations(self):
        for question in [
            "ನನ್ನ ಟೊಮೆಟೋ ಗಿಡಕ್ಕೆ ನೀರು ಸಾಲದೆ ಒಣಗುತ್ತಿದೆ.",
            "ಟೊಮೆಟೋ ಗಿಡದ ಮಣ್ಣು ಒಣಗಿದೆ.",
        ]:
            self.assert_kannada_topic(question, "water_stress", "tomato-water-stress-001")

    def test_whitefly_observation_variations(self):
        for question in [
            "ನನ್ನ ಟೊಮೆಟೋ ಎಲೆಗಳ ಕೆಳಗೆ ಚಿಕ್ಕ ಬಿಳಿ ಕೀಟಗಳು ಕಾಣಿಸುತ್ತಿವೆ.",
            "ಟೊಮೆಟೋ ಎಲೆಗಳ ಕೆಳಗೆ ಬಿಳಿ ಹುಳುಗಳಿವೆಯೇ ಎಂದು ನೋಡಿದೆ.",
        ]:
            self.assert_kannada_topic(question, "whitefly_observation", "tomato-whitefly-001")

    def test_fruit_borer_observation_variations(self):
        for question in [
            "ನನ್ನ ಟೊಮೆಟೋ ಹಣ್ಣುಗಳಲ್ಲಿ ರಂಧ್ರಗಳಿವೆ.",
            "ಟೊಮೆಟೋ ಹಣ್ಣಿನೊಳಗೆ ಕುಳಿ ಮತ್ತು ಪುಡಿ ಕಾಣುತ್ತಿದೆ.",
        ]:
            self.assert_kannada_topic(question, "fruit_borer_observation", "tomato-fruit-borer-001")

    def test_leaf_miner_observation_variations(self):
        for question in [
            "ನನ್ನ ಟೊಮೆಟೋ ಎಲೆಗಳ ಒಳಗೆ ಹಾವಿನಂತೆ ಗೆರೆಗಳಿವೆ.",
            "ಟೊಮೆಟೋ ಎಲೆಗಳಲ್ಲಿ ಸರ್ಪದಂತೆ ಗೆರೆಗಳು ಕಾಣುತ್ತಿವೆ.",
        ]:
            self.assert_kannada_topic(question, "leaf_miner_observation", "tomato-leaf-miner-001")

    def test_existing_spots_curling_and_fruit_damage(self):
        cases = [
            ("ಟೊಮೆಟೋ ಎಲೆಗಳಲ್ಲಿ ಕಂದು ಕಲೆಗಳಿವೆ.", "brown_spots", "tomato-leaf-yellowing-001"),
            ("ಟೊಮೆಟೋ ಎಲೆಗಳು ಮುರುಕಾಗುತ್ತಿವೆ.", "leaf_curling", "tomato-leaf-yellowing-001"),
            ("ನನ್ನ ಟೊಮೆಟೋ ಹಣ್ಣುಗಳು ಹಾನಿಯಾಗಿದೆ.", "fruit_damage", "tomato-fruit-borer-001"),
        ]
        for question, symptom, record_id in cases:
            self.assert_kannada_topic(question, symptom, record_id)

    def test_ambiguous_kannada_question_asks_for_details(self):
        guidance = build_guidance("ನನ್ನ ಟೊಮೆಟೋ ಗಿಡ ಸರಿಯಿಲ್ಲ.", "ಕನ್ನಡ (Kannada)")
        self.assertEqual(guidance["sources"], [])
        self.assertTrue(guidance["follow_up_questions"])
        self.assertIn("ಇನ್ನಷ್ಟು ಮಾಹಿತಿ", guidance["understanding"])

    def test_kannada_safety_stays_active(self):
        self.assertIsNotNone(validate_safety("ಟೊಮೆಟೋಗೆ ಔಷಧಿ ಎಷ್ಟು ಹಾಕಬೇಕು?"))
        guidance = build_guidance("ಟೊಮೆಟೋಗೆ ಔಷಧಿ ಎಷ್ಟು ಹಾಕಬೇಕು?", "ಕನ್ನಡ (Kannada)")
        self.assertEqual(guidance["sources"], [])
        self.assertIn("not a confirmed diagnosis", guidance["uncertainty"])


if __name__ == "__main__":
    unittest.main()
