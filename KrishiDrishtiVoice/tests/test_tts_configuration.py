import unittest
from unittest.mock import patch

import gnani_service


class FakeResponse:
    def __init__(self, *, status_code=200, content=b"RIFFtest", content_type="audio/wav", text=""):
        self.status_code = status_code
        self.content = content
        self.headers = {"Content-Type": content_type}
        self.text = text
        self.ok = 200 <= status_code < 400


class TimbreConfigurationTests(unittest.TestCase):
    def test_documented_language_and_voice_defaults(self):
        self.assertEqual(gnani_service.TTS_LANGUAGE_CODES["ಕನ್ನಡ (Kannada)"], "kn-IN")
        self.assertEqual(gnani_service.TTS_LANGUAGE_CODES["English"], "en-IN")
        self.assertEqual(gnani_service.TTS_LANGUAGE_CODES["Hindi"], "hi-IN")
        self.assertEqual(gnani_service.TTS_VOICES["ಕನ್ನಡ (Kannada)"], "Nalini")
        self.assertEqual(gnani_service.TTS_VOICES["English"], "Kaveri")
        self.assertEqual(gnani_service.TTS_VOICES["Hindi"], "Nalini")

    @patch("gnani_service.requests.post")
    @patch("gnani_service._api_key", return_value="test-key")
    def test_kannada_payload_keeps_existing_mapping(self, _key, post):
        post.return_value = FakeResponse()
        result = gnani_service.synthesize_speech("ಪರೀಕ್ಷೆ", "ಕನ್ನಡ (Kannada)")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(post.call_args.kwargs["json"]["language"], "kn-IN")
        self.assertEqual(post.call_args.kwargs["json"]["voice"], "Nalini")

    @patch("gnani_service.requests.post")
    @patch("gnani_service._api_key", return_value="test-key")
    def test_english_payload_uses_documented_default(self, _key, post):
        post.return_value = FakeResponse()
        result = gnani_service.synthesize_speech("Test message", "English")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(post.call_args.kwargs["json"]["language"], "en-IN")
        self.assertEqual(post.call_args.kwargs["json"]["voice"], "Kaveri")

    @patch("gnani_service.requests.post")
    @patch("gnani_service._api_key", return_value="test-key")
    def test_hindi_payload_uses_documented_default(self, _key, post):
        post.return_value = FakeResponse()
        result = gnani_service.synthesize_speech("परीक्षण संदेश", "Hindi")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(post.call_args.kwargs["json"]["language"], "hi-IN")
        self.assertEqual(post.call_args.kwargs["json"]["voice"], "Nalini")

    @patch("gnani_service._api_key", return_value=None)
    def test_missing_credentials_prevents_request(self, _key):
        with patch("gnani_service.requests.post") as post:
            result = gnani_service.synthesize_speech("Test", "English")
        self.assertIn("credentials", result.error.lower())
        post.assert_not_called()

    @patch("gnani_service._api_key", return_value="test-key")
    def test_unsupported_language_prevents_request(self, _key):
        with patch("gnani_service.requests.post") as post:
            result = gnani_service.synthesize_speech("Test", "Tamil")
        self.assertIn("not enabled", result.error)
        post.assert_not_called()

    @patch("gnani_service.requests.post")
    @patch("gnani_service._api_key", return_value="test-key")
    def test_api_error_returns_sanitized_diagnostic(self, _key, post):
        post.return_value = FakeResponse(
            status_code=400,
            content=b"",
            content_type="application/json",
            text='{"message":"invalid payload","api_key":"secret"}',
        )
        result = gnani_service.synthesize_speech("Test", "English")
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.diagnostic["content_type"], "application/json")
        self.assertIn("[REDACTED]", result.diagnostic["body"])
        self.assertNotIn("secret", result.diagnostic["body"])


if __name__ == "__main__":
    unittest.main()
