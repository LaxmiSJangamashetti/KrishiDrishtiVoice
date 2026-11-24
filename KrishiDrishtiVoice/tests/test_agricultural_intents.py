import unittest

from agriculture_engine import build_guidance, classify_intent, search


class AgriculturalIntentTests(unittest.TestCase):
    def test_crop_only_questions_do_not_retrieve_disease_records(self):
        for question, crop, intent in (
            ("How can I grow more chilli plants?", "chilli", "cultivation"),
            ("How can I increase tomato yield?", "tomato", "productivity"),
            ("How should I plant maize?", "maize", "cultivation"),
            ("How can I grow potatoes?", "potato", "cultivation"),
            ("When should I water my paddy?", "rice", "irrigation"),
        ):
            with self.subTest(question=question):
                guidance = build_guidance(question)
                self.assertEqual(guidance["crop"], crop)
                self.assertEqual(guidance["intent"], intent)
                self.assertFalse(any("disease" in match.record.get("category", "") or "symptom" in match.record.get("category", "") for match in search(question)))

    def test_symptom_and_service_intents_remain_distinct(self):
        self.assertEqual(classify_intent("My chilli leaves are curling", "leaf_curling"), "symptom_investigation")
        self.assertEqual(build_guidance("What is today's tomato price?")["intent"], "market_price")
        self.assertEqual(build_guidance("Will it rain on my farm?")["intent"], "weather")

    def test_kannada_cultivation_question_is_not_a_disease_report(self):
        guidance = build_guidance("ಹೆಚ್ಚು ಮೆಣಸಿನ ಗಿಡಗಳನ್ನು ಹೇಗೆ ಬೆಳೆಸುವುದು?")
        self.assertEqual(guidance["crop"], "chilli")
        self.assertEqual(guidance["intent"], "cultivation")
        matches = search("ಹೆಚ್ಚು ಮೆಣಸಿನ ಗಿಡಗಳನ್ನು ಹೇಗೆ ಬೆಳೆಸುವುದು?")
        self.assertTrue(matches)
        self.assertTrue(all(match.record.get("category") == "cultivation_guidance" for match in matches))


if __name__ == "__main__":
    unittest.main()
