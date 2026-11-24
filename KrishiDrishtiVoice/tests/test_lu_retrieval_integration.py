import unittest

from agriculture_engine import build_guidance, search
from language_understanding import understand


class StructuredRetrievalIntegrationTests(unittest.TestCase):
    def test_structured_lu_drives_retrieval(self):
        text = "My tomato leaves are turning yellow"
        lu = understand(text)
        matches = search(text, lu_result=lu)
        self.assertTrue(matches)
        self.assertEqual(matches[0].record["id"], "tomato-leaf-yellowing-001")

    def test_absent_symptom_is_not_used_for_retrieval(self):
        text = "My tomato leaves are not yellow"
        lu = understand(text)
        matches = search(text, lu_result=lu)
        self.assertFalse(any(m.record["id"] == "tomato-leaf-yellowing-001" for m in matches))

    def test_safety_flags_block_guidance_retrieval_path(self):
        text = "What pesticide dose should I use for tomato?"
        lu = understand(text)
        guidance = build_guidance(text, lu_result=lu)
        self.assertEqual(guidance["sources"], [])
        self.assertTrue(guidance.get("safety_category"))


if __name__ == "__main__":
    unittest.main()
