import io
import unittest

from PIL import Image

from image_processing import load_image_bytes, validate_image


def png_bytes(color=(80, 120, 60)):
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), color).save(buffer, format="PNG")
    return buffer.getvalue()


class ImageProcessingTests(unittest.TestCase):
    def test_valid_image_loads_and_converts_to_rgb(self):
        image = load_image_bytes(png_bytes())
        self.assertEqual(image.mode, "RGB")

    def test_corrupt_image_is_rejected(self):
        report = validate_image(b"not-an-image")
        self.assertFalse(report.accepted)
        self.assertEqual(report.status, "rejected")

    def test_excessive_file_size_is_rejected(self):
        report = validate_image(png_bytes(), max_bytes=10)
        self.assertFalse(report.accepted)

    def test_dark_image_gets_retake_feedback(self):
        report = validate_image(png_bytes((0, 0, 0)))
        self.assertFalse(report.accepted)
        self.assertTrue(any("dark" in reason.lower() for reason in report.reasons))


if __name__ == "__main__":
    unittest.main()
