import unittest

from language_understanding import LUContext, understand, validate_lu


class LanguageUnderstandingTests(unittest.TestCase):
    def test_kannada_evidence_and_schema(self):
        text = "ನನ್ನ ಟೊಮೆಟೋ ಗಿಡದ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ"
        result = understand(text, message_id="m-kn")
        self.assertTrue(validate_lu(result)[0])
        self.assertEqual(result["schema_version"], "1.0.0")
        self.assertEqual(result["observations"][0]["normalized_value"], "tomato")
        symptom = next(o for o in result["observations"] if o["kind"] == "symptom")
        self.assertEqual(symptom["normalized_value"], "leaf_yellowing")
        self.assertEqual(symptom["evidence"][0]["message_id"], "m-kn")
        self.assertIn("ಹಳದಿ", symptom["evidence"][0]["phrase"])

    def test_multiple_observations_have_unique_ids(self):
        result = understand("My tomato leaves are yellow and have brown spots", message_id="m-multi")
        ids = [o["observation_id"] for o in result["observations"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(any(o["normalized_value"] == "leaf_yellowing" for o in result["observations"]))
        self.assertTrue(any(o["normalized_value"] == "brown_spots" for o in result["observations"]))

    def test_negated_symptom_is_not_present(self):
        result = understand("My tomato leaves are not yellow")
        symptom = next(o for o in result["observations"] if o["kind"] == "symptom")
        self.assertEqual(symptom["polarity"], "absent")

    def test_code_mixed_language_is_reported(self):
        result = understand("ನನ್ನ tomato leaves are yellow")
        self.assertTrue(result["language"]["code_mixed"])
        self.assertTrue(any(o["normalized_value"] == "tomato" for o in result["observations"]))

    def test_safety_flags_are_independent(self):
        result = understand("What pesticide dose should I use for tomato and can I mix chemicals?")
        self.assertIn("REQUESTS_PESTICIDE_DOSE", result["lu_safety_flags"])
        self.assertIn("REQUESTS_CHEMICAL_MIXING", result["lu_safety_flags"])
        self.assertEqual(result["abstention"]["required"], True)

    def test_missing_crop_is_explicit(self):
        result = understand("The leaves are curling")
        self.assertIn({"field": "crop", "state": "not_mentioned"}, result["missing_information"])
        self.assertFalse(any(o["kind"] == "crop" for o in result["observations"]))

    def test_unknown_input_abstains(self):
        result = understand("When will the market price change?")
        self.assertTrue(result["abstention"]["required"])
        self.assertEqual(result["observations"], [])

    def test_context_retains_unmentioned_observation(self):
        first = understand("My tomato leaves are yellow", message_id="m1")
        context = LUContext(observations={o["observation_id"]: o for o in first["observations"]})
        second = understand("The soil is wet", message_id="m2", context=context)
        self.assertTrue(any(o["normalized_value"] == "leaf_yellowing" for o in second["observations"]))
        self.assertTrue(any(o["normalized_value"] == "waterlogging" for o in second["observations"]))

    def test_contrast_keeps_negative_and_positive_observations_separate(self):
        result = understand("ಟೊಮೆಟೋ ಎಲೆ ಹಳದಿ ಆಗಿಲ್ಲ, ಆದರೆ ಕಂದು ಕಲೆಗಳಿವೆ")
        values = {o["normalized_value"]: o["polarity"] for o in result["observations"]}
        self.assertEqual(values.get("leaf_yellowing"), "absent")
        self.assertEqual(values.get("brown_spots"), "present")

    def test_specific_observation_suppresses_broad_duplicate(self):
        result = understand("ಟೊಮೆಟೋ ಗಿಡದಲ್ಲಿ ಬಿಳಿ ಹುಳು ಕಾಣುತ್ತಿದೆ")
        values = [o["normalized_value"] for o in result["observations"]]
        self.assertIn("whitefly_observation", values)
        self.assertNotIn("insects", values)

    def test_code_mixed_and_colloquial_forms(self):
        result = understand("ನನ್ನ tomato plants wilting ಆಗ್ತಿವೆ")
        self.assertTrue(any(o["normalized_value"] == "tomato" for o in result["observations"]))
        self.assertTrue(any(o["normalized_value"] == "wilting" for o in result["observations"]))


if __name__ == "__main__":
    unittest.main()
