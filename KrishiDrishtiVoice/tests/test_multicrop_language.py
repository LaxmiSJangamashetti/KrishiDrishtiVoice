import unittest

from agriculture_engine import build_guidance, parse_question
from crop_registry import get_crop_capability, supported_crop_names


class MulticropLanguageTests(unittest.TestCase):
    def test_priority_crop_aliases(self):
        cases = {
            "My potato leaves are developing brown spots": "potato",
            "My maize plants are turning yellow": "maize",
            "ನನ್ನ ಮೆಣಸಿನಕಾಯಿ ಎಲೆಗಳು ಮುರುಕಾಗಿವೆ": "chilli",
            "ನನ್ನ ಭತ್ತದ ಎಲೆ ತುದಿಗಳು ಒಣಗುತ್ತಿವೆ": "rice",
        }
        for question, expected in cases.items():
            with self.subTest(question=question):
                self.assertEqual(parse_question(question)["crop"], expected)
                self.assertEqual(build_guidance(question)["crop"], expected)

    def test_crop_capability_flags_do_not_claim_image_support(self):
        self.assertEqual(supported_crop_names(), ["tomato", "rice", "potato", "maize", "chilli"])
        for crop in supported_crop_names():
            with self.subTest(crop=crop):
                self.assertEqual(get_crop_capability(crop)["image_supported"], crop == "tomato")

    def test_rice_does_not_match_price(self):
        self.assertIsNone(parse_question("When will the market price change?")["crop"])


if __name__ == "__main__":
    unittest.main()
