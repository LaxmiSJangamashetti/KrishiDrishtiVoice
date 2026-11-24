import unittest
from unittest.mock import patch

import market_service
from market_service import MarketServiceError


class Response:
    def __init__(self, status=200, payload=None):
        self.status_code = status
        self._payload = payload

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class MarketServiceTests(unittest.TestCase):
    def setUp(self):
        market_service.clear_cache()

    @patch("market_service.requests.get")
    def test_all_five_endpoints_parse_documented_envelopes(self, get):
        row = {"state": "Karnataka", "market": "Bengaluru APMC", "commodity": "Tomato", "arrival_date": "2026-11-24", "min_price": 1000, "max_price": 1800, "modal_price": 1400}
        get.side_effect = [Response(payload={"success": True, "data": ["Karnataka"]}), Response(payload={"success": True, "data": ["Tomato"]}), Response(payload={"success": True, "data": [{"market": "Bengaluru APMC", "district": "Bengaluru"}]}), Response(payload={"success": True, "data": [row]}), Response(payload={"success": True, "data": [row]})]
        self.assertEqual(market_service.states(), ["Karnataka"])
        self.assertEqual(market_service.commodities(state="Karnataka"), ["Tomato"])
        self.assertEqual(market_service.markets(state="Karnataka")[0]["district"], "Bengaluru")
        self.assertEqual(market_service.prices(state="Karnataka", commodity="Tomato")["data"][0]["modal_price"], 1400)
        self.assertEqual(len(market_service.price_history(state="Karnataka", commodity="Tomato")["data"]), 1)
        self.assertEqual(get.call_count, 5)

    @patch("market_service.requests.get")
    def test_rate_limit_is_safe(self, get):
        get.return_value = Response(status=429, payload={"success": False, "error": "rate"})
        with self.assertRaisesRegex(MarketServiceError, "rate limit"):
            market_service.states()

    @patch("market_service.requests.get")
    def test_malformed_and_empty_responses(self, get):
        get.return_value = Response(payload={"success": True})
        with self.assertRaisesRegex(MarketServiceError, "missing data"):
            market_service.states()
        market_service.clear_cache()
        get.return_value = Response(payload={"success": True, "data": []})
        self.assertEqual(market_service.states(), [])

    def test_validation_and_intent(self):
        with self.assertRaisesRegex(MarketServiceError, "Unsupported state"):
            market_service.markets(state="Unknown")
        with self.assertRaisesRegex(MarketServiceError, "state or commodity"):
            market_service.prices()
        self.assertTrue(market_service.is_market_query("ಇವತ್ತು ಟೊಮೇಟೊ ಬೆಲೆ ಎಷ್ಟು?"))
        self.assertTrue(market_service.is_market_query("What is today's market price?"))
        self.assertFalse(market_service.is_market_query("My tomato leaves are yellow"))


if __name__ == "__main__":
    unittest.main()
