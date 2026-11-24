import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from image_processing.inference_engine import infer_image
from image_processing.model_registry import ModelUnavailable, get_model_config, load_model_metadata, verify_weight_checksum


class ModelRegistryTests(unittest.TestCase):
    def test_multicrop_model_registry_entries(self):
        for crop in ("tomato", "potato", "maize"):
            with self.subTest(crop=crop):
                config = get_model_config(crop)
                self.assertIsNotNone(config)
                self.assertEqual(config["status"], "experimental")
        self.assertIsNone(get_model_config("rice"))
        self.assertIsNone(get_model_config("chilli"))

    def test_non_tomato_artifacts_are_crop_named_and_checksummed(self):
        expected = {
            "potato": "mobilenet_v3_small_potato.onnx",
            "maize": "mobilenet_v3_small_maize.onnx",
        }
        for crop, filename in expected.items():
            with self.subTest(crop=crop):
                config = get_model_config(crop)
                metadata = load_model_metadata(config["metadata"])
                artifact = Path(metadata["onnx_model_path"])
                self.assertEqual(artifact.name, filename)
                self.assertEqual(len(metadata["onnx_sha256"]), 64)
                self.assertRegex(metadata["onnx_sha256"], r"^[0-9a-fA-F]{64}$")
                self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), metadata["onnx_sha256"])
                self.assertEqual(metadata["export_source_model_version"], f"{crop}-mobilenet-v3-small-exp1")

    def test_export_metadata_has_runtime_and_calibration_contract(self):
        path = Path(r"D:\KrishiDrishtiML\models\tomato_full_exp2\export\metadata.json")
        if not path.exists():
            self.skipTest("experimental export is not installed")
        metadata = load_model_metadata(path)
        self.assertEqual(metadata["runtime_format"], "onnx")
        self.assertIn("calibration", metadata)
        self.assertIn("rejection", metadata)

    def test_corrupted_onnx_checksum_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.onnx"; path.write_bytes(b"bad")
            with self.assertRaises(ModelUnavailable):
                verify_weight_checksum(path, {"weights_sha256": "wrong"})

    def test_missing_model_abstains(self):
        result = infer_image(image_id="img-1", image_bytes=b"", weights_path="missing.bin", metadata_path="missing.json")
        self.assertTrue(result.abstained)
        self.assertEqual(result.supported_class_status, "unknown")

    def test_incomplete_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metadata.json"
            path.write_text(json.dumps({"model_version": "x"}), encoding="utf-8")
            with self.assertRaises(ModelUnavailable):
                load_model_metadata(path)

    def test_checksum_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "weights.bin"; path.write_bytes(b"weights")
            with self.assertRaises(ModelUnavailable):
                verify_weight_checksum(path, {"weights_sha256": "wrong"})


if __name__ == "__main__":
    unittest.main()
