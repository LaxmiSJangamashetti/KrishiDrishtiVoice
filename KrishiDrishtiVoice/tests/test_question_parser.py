import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from agriculture_engine import normalize_text, parse_question


class QuestionParserTests(unittest.TestCase):
    def test_english_symptoms(self):
        cases = {
            "My tomato leaves are turning yellow.": "leaf_yellowing", "My tomato plant is wilting.": "wilting",
            "My tomato leaves have brown spots.": "brown_spots", "My tomato leaves are curling.": "leaf_curling",
            "My tomato plant is drying even though the soil is wet.": "wet_soil_drying", "My tomato crop has insects.": "insects", "My tomato fruits are damaged.": "fruit_damage",
        }
        for question, expected in cases.items():
            with self.subTest(question=question):
                parsed = parse_question(question)
                self.assertEqual(parsed["crop"], "tomato")
                self.assertEqual(parsed["symptom"], expected)

    def test_kannada_symptoms_and_unicode(self):
        cases = {"ನನ್ನ ಟೊಮೆಟೋ ಗಿಡದ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ.": "leaf_yellowing", "ನನ್ನ ಟೊಮೆಟೋ ಗಿಡ ಒಣಗುತ್ತಿದೆ.": "wilting", "ನನ್ನ ಟೊಮೆಟೋ ಗಿಡದ ಎಲೆಗಳಲ್ಲಿ ಕಲೆಗಳಿವೆ.": "brown_spots"}
        for question, expected in cases.items():
            with self.subTest(question=question):
                parsed = parse_question(question)
                self.assertEqual(parsed["crop"], "tomato")
                self.assertEqual(parsed["symptom"], expected)
                self.assertIn("ಟೊಮೆಟೋ", parsed["normalized_text"])

    def test_unknown_question_is_not_forced(self):
        parsed = parse_question("My plant is unhealthy.")
        self.assertIsNone(parsed["crop"])
        self.assertIsNone(parsed["symptom"])

    def test_normalization_preserves_kannada(self):
        self.assertIn("ಹಳದಿ", normalize_text("ಹಳದಿ"))


if __name__ == "__main__":
    unittest.main()
