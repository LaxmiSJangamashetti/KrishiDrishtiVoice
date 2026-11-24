import unittest

from crop_registry import get_crop_capability, supported_crop_names


class CropRegistryTests(unittest.TestCase):
    def test_five_priority_crops_are_guidance_supported(self):
        self.assertEqual(supported_crop_names(), ["tomato", "rice", "potato", "maize", "chilli"])
        self.assertTrue(get_crop_capability("tomato")["guidance_supported"])

    def test_rice_is_registered_with_limited_guidance_support(self):
        rice = get_crop_capability("rice")
        self.assertTrue(rice["registered"])
        self.assertTrue(rice["recognized"])
        self.assertTrue(rice["guidance_supported"])


if __name__ == "__main__":
    unittest.main()
