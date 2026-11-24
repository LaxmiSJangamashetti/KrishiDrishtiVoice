import unittest

from agriculture_engine import search
from language_understanding import understand


class Phase2KnowledgeTests(unittest.TestCase):
    def test_rice_question_retrieves_rice_record(self):
        matches = search("My rice leaves are yellow")
        self.assertTrue(matches)
        self.assertTrue(all(match.record["crop"] == "rice" for match in matches))

    def test_structured_match_has_traceable_reason(self):
        text = "My tomato leaves are turning yellow"
        matches = search(text, lu_result=understand(text))
        self.assertTrue(matches)
        self.assertTrue(any("symptom_record_match" in match.reasons for match in matches))

    def test_negative_observation_does_not_rank_symptom_record(self):
        text = "My tomato leaves are not yellow"
        matches = search(text, lu_result=understand(text))
        self.assertFalse(any(match.record["id"] == "tomato-leaf-yellowing-001" for match in matches))


if __name__ == "__main__":
    unittest.main()
