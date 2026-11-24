import unittest

from image_processing_contract import ImageResult


class ImageProcessingContractTests(unittest.TestCase):
    def test_safe_default_is_abstention(self):
        result = ImageResult(image_id="img-1")
        self.assertEqual(result.validate(), [])
        self.assertTrue(result.to_dict()["abstained"])

    def test_confidence_and_enum_validation(self):
        result = ImageResult(image_id="img-2", model_confidence=1.2)
        self.assertIn("model_confidence must be between 0 and 1", result.validate())

    def test_no_unqualified_non_abstained_result(self):
        result = ImageResult(image_id="img-3", abstained=False)
        self.assertIn("non-abstained results require an uncertainty_reason", result.validate())


if __name__ == "__main__":
    unittest.main()
