import os
import tempfile
import unittest
from pathlib import Path

import farmer_profile.repository as repository


class FarmerProfileRepositoryTests(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.db_path = Path(temp_dir.name) / "profiles.sqlite3"
        os.environ["KRISHIDRISHTI_PROFILE_DB"] = str(self.db_path)
        repository.initialize_database()

    def tearDown(self):
        os.environ.pop("KRISHIDRISHTI_PROFILE_DB", None)

    def test_profile_and_profile_update(self):
        profile_id = repository.save_profile({"name": "Test Farmer", "mobile": "9876543210", "pin_code": "560001"})
        profile = repository.get_profile()
        self.assertEqual(profile["id"], profile_id)
        self.assertEqual(profile["name"], "Test Farmer")

        repository.save_profile({"name": "Updated Farmer", "mobile": "9876543210", "pin_code": "560001"})
        self.assertEqual(repository.get_profile()["name"], "Updated Farmer")

    def test_farm_and_crop_crud(self):
        repository.save_profile({"name": "Test Farmer"})
        farm_id = repository.save_farm({"name": "Test Farm", "area": 2.5, "area_unit": "acre"})
        farms = repository.list_farms()
        self.assertEqual(len(farms), 1)

        crop_id = repository.save_crop({"name": "Tomato", "farm_id": farm_id, "status": "Active"})
        crops = repository.list_crops()
        self.assertEqual(len(crops), 1)
        self.assertEqual(crops[0]["farm_name"], "Test Farm")

        repository.delete_crop(crop_id)
        repository.delete_farm(farm_id)
        self.assertEqual(repository.list_crops(), [])
        self.assertEqual(repository.list_farms(), [])

    def test_blank_name_is_rejected_by_repository_contract(self):
        with self.assertRaises(Exception):
            repository.save_profile({"name": "   "})

    def test_consultation_persists(self):
        repository.save_profile({"name": "Test Farmer"})
        repository.save_consultation("Tomato question", "What about yellow leaves?", "Observation-only guidance", None, None, "English")
        consultations = repository.list_consultations()
        self.assertEqual(len(consultations), 1)
        self.assertEqual(consultations[0]["question"], "What about yellow leaves?")

    def test_farm_coordinates_persist_in_isolated_database(self):
        repository.save_profile({"name": "Coordinate Farmer"})
        farm_id = repository.save_farm({"name": "Mapped Farm", "latitude": 12.9716, "longitude": 77.5946, "boundary_coordinates": "[[12.97,77.59],[12.98,77.60]]"})
        farm = repository.list_farms()[0]
        self.assertEqual(farm["id"], farm_id)
        self.assertAlmostEqual(farm["latitude"], 12.9716)
        self.assertAlmostEqual(farm["longitude"], 77.5946)
        self.assertIn("12.97", farm["boundary_coordinates"])


if __name__ == "__main__":
    unittest.main()
