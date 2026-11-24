import unittest
from unittest.mock import Mock, patch

import requests

from agromonitoring_service import AgroMonitoringError, clear_cache, current_weather, temperature_celsius, weather_forecast


class AgroMonitoringServiceTests(unittest.TestCase):
    def setUp(self):
        clear_cache()

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_key_fails_without_request(self):
        with self.assertRaisesRegex(AgroMonitoringError, "not configured"):
            current_weather(lat=12.9, lon=77.6)

    @patch.dict("os.environ", {"AGROMONITORING_API_KEY": "test-key"})
    @patch("agromonitoring_service.requests.get")
    def test_auth_error_is_safe(self, get):
        get.return_value.status_code = 401
        with self.assertRaisesRegex(AgroMonitoringError, "authorization failed"):
            current_weather(lat=12.9, lon=77.6)
        self.assertTrue(get.called)

    @patch.dict("os.environ", {"AGROMONITORING_API_KEY": "test-key"})
    @patch("agromonitoring_service.requests.get")
    def test_current_weather_documented_object_and_optional_rain(self, get):
        response = Mock(status_code=200)
        response.json.return_value = {"dt": 1, "weather": [{"description": "clear sky"}], "main": {"temp": 298.15, "humidity": 70}, "wind": {"speed": 2.0}}
        get.return_value = response
        value = current_weather(lat=12.9, lon=77.6)
        self.assertEqual(value["main"]["humidity"], 70)
        self.assertIsNone(value.get("rain"))
        self.assertEqual(get.call_args.kwargs["params"], {"lat": 12.9, "lon": 77.6, "appid": "test-key"})

    @patch.dict("os.environ", {"AGROMONITORING_API_KEY": "test-key"})
    @patch("agromonitoring_service.requests.get")
    def test_forecast_is_documented_array(self, get):
        response = Mock(status_code=200)
        response.json.return_value = [{"dt": 2, "main": {"temp": 293.15}, "weather": []}]
        get.return_value = response
        self.assertEqual(len(weather_forecast(lat=12.9, lon=77.6)), 1)

    @patch.dict("os.environ", {"AGROMONITORING_API_KEY": "test-key"})
    @patch("agromonitoring_service.requests.get")
    def test_forecast_and_current_failures_are_independent(self, get):
        current = Mock(status_code=200)
        current.json.return_value = {"dt": 1, "main": {"temp": 293.15}, "weather": []}
        get.return_value = current
        self.assertIsNotNone(current_weather(lat=1, lon=2))
        get.side_effect = requests.Timeout()
        with self.assertRaisesRegex(AgroMonitoringError, "timed out"):
            weather_forecast(lat=1, lon=2)

    @patch.dict("os.environ", {"AGROMONITORING_API_KEY": "test-key"})
    @patch("agromonitoring_service.requests.get")
    def test_safe_categories_invalid_json_subscription_and_rate_limit(self, get):
        response = Mock(status_code=403)
        response.json.return_value = {"message": "plan restriction"}
        get.return_value = response
        with self.assertRaisesRegex(AgroMonitoringError, "account plan") as caught:
            current_weather(lat=1, lon=2)
        self.assertEqual(caught.exception.category, "subscription_restriction")
        clear_cache()
        response.status_code = 429
        with self.assertRaisesRegex(AgroMonitoringError, "rate limit"):
            current_weather(lat=1, lon=2)
        clear_cache()
        response.status_code = 200
        response.json.side_effect = ValueError()
        with self.assertRaisesRegex(AgroMonitoringError, "invalid JSON"):
            current_weather(lat=1, lon=2)

    @patch.dict("os.environ", {"AGROMONITORING_API_KEY": "secret-key"})
    @patch("agromonitoring_service.requests.get")
    def test_unexpected_structure_and_credentials_are_not_in_errors(self, get):
        response = Mock(status_code=200)
        response.json.return_value = []
        get.return_value = response
        with self.assertRaisesRegex(AgroMonitoringError, "not an object") as caught:
            current_weather(lat=1, lon=2)
        self.assertNotIn("secret-key", str(caught.exception))

    def test_temperature_conversion_is_single_and_documented(self):
        self.assertEqual(temperature_celsius(293.15), 20.0)
        self.assertIsNone(temperature_celsius(None))


if __name__ == "__main__":
    unittest.main()
