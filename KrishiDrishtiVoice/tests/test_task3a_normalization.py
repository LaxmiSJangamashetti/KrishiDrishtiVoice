import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from agriculture_engine import normalize_text, parse_question


class Task3ANormalizationTests(unittest.TestCase):
    def test_aliases_preserve_known_crop_and_colloquial_forms(self):
        parsed = parse_question("ನನ್ನ ಟೊಮೇಟೊ ಗಿಡ ಬಾಡ್ತಾ ಇದೆ")
        self.assertEqual(parsed["crop"], "tomato")
        self.assertEqual(parsed["symptom"], "wilting")

    def test_code_mixed_tomato_leaf_alias(self):
        self.assertEqual(parse_question("Tomato ele haladi agtide")["crop"], "tomato")

    def test_negated_symptoms_do_not_activate(self):
        for text in ("ಎಲೆ ಹಳದಿ ಆಗಿಲ್ಲ", "ಗಿಡ ಬಾಡುತ್ತಿಲ್ಲ", "ಕೀಟ ಇಲ್ಲ", "ಮಣ್ಣು ಒಣಗಿಲ್ಲ"):
            self.assertIsNone(parse_question(text)["symptom"])

    def test_black_is_not_brown(self):
        self.assertIsNone(parse_question("ಟೊಮೆಟೋ ಗಿಡದಲ್ಲಿ ಕಪ್ಪು ಕಲೆ ಇದೆ")["symptom"])

    def test_original_input_is_not_mutated(self):
        original = "ಟೊಮೇಟೊ ಎಲೆ ಹಳದಿ ಆಗ್ತಿದೆ"
        self.assertIn("ಟೊಮೆಟೋ", normalize_text(original))
        self.assertEqual(original, "ಟೊಮೇಟೊ ಎಲೆ ಹಳದಿ ಆಗ್ತಿದೆ")


if __name__ == "__main__":
    unittest.main()
