import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
from agriculture_engine import build_guidance, validate_safety


class SafetyValidatorTests(unittest.TestCase):
    def test_unsafe_requests_are_rejected(self):
        cases = ["What pesticide dosage should I use?", "How do I mix chemical treatments?", "How much fertilizer should I use?", "Give me a guaranteed disease diagnosis.", "What is the best medicine to cure this?"]
        for question in cases:
            with self.subTest(question=question):
                self.assertIsNotNone(validate_safety(question))
                guidance = build_guidance(question)
                self.assertIn("cannot provide", guidance["understanding"])
                self.assertEqual(guidance["sources"], [])

    def test_crop_context_is_required_for_unsafe_guidance(self):
        guidance = build_guidance("How much fertilizer should I use for tomato?")
        self.assertIn("cannot provide", guidance["understanding"])

    def test_engine_is_offline(self):
        with patch.dict(sys.modules, {"requests": None}):
            guidance = build_guidance("My tomato leaves are turning yellow.")
        self.assertEqual(guidance["crop"], "tomato")
        self.assertTrue(guidance["sources"])


if __name__ == "__main__":
    unittest.main()
