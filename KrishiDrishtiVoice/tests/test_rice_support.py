import unittest

from agriculture_engine import build_guidance, parse_question, search
from language_understanding import understand


class RiceSupportTests(unittest.TestCase):
    def test_english_paddy_question_preserves_crop_and_symptom(self):
        question = "What to do if my paddy plants are getting yellow?"
        parsed = parse_question(question)
        self.assertEqual(parsed["crop"], "rice")
        self.assertEqual(parsed["symptom"], "leaf_yellowing")
        guidance = build_guidance(question)
        self.assertEqual(guidance["crop"], "rice")
        self.assertTrue(guidance["sources"])
        self.assertNotIn("Which crop", " ".join(guidance["follow_up_questions"]))

    def test_kannada_rice_question_is_recognized(self):
        result = understand("ನನ್ನ ಭತ್ತದ ಬೆಳೆಯ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ", message_id="rice-kn")
        self.assertTrue(any(o["normalized_value"] == "rice" for o in result["observations"]))
        self.assertTrue(any(o["normalized_value"] == "leaf_yellowing" for o in result["observations"]))
        self.assertEqual(search("ನನ್ನ ಭತ್ತದ ಬೆಳೆಯ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ", lu_result=result)[0].record["crop"], "rice")

    def test_yellowing_does_not_confirm_nitrogen_deficiency(self):
        guidance = build_guidance("My paddy plants are getting yellow")
        self.assertIn("not a confirmed diagnosis", guidance["uncertainty"])
        self.assertTrue(any("Do not assume nitrogen deficiency" in action for action in guidance["safe_actions"]))

    def test_price_does_not_trigger_rice_alias(self):
        result = understand("When will the market price change?")
        self.assertEqual(result["observations"], [])
        self.assertTrue(result["abstention"]["required"])


if __name__ == "__main__":
    unittest.main()
