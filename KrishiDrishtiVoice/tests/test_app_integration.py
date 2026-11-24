import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitIntegrationTests(unittest.TestCase):
    def test_app_renders_without_exception(self):
        app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertTrue(app.radio)
        self.assertIn("Namaskara", " ".join(item.value for item in app.markdown if hasattr(item, "value")))

    def test_farmer_dashboard_navigation_renders(self):
        app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=20).run()
        app.radio[0].set_value("Ask KrishiDrishti").run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Ask KrishiDrishti" in str(item.value) for item in app.title))

    def test_crop_image_analysis_route_is_honest_without_model(self):
        app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=20).run()
        app.radio[0].set_value("Crop Image Analysis").run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Crop Image Analysis" in str(item.value) for item in app.title))


if __name__ == "__main__":
    unittest.main()
