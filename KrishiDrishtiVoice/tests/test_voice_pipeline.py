import io
import unittest
from unittest.mock import Mock, patch

import gnani_service
from conversation_manager import new_conversation, process_turn


class FakeAudio:
    name = "test.wav"
    type = "audio/wav"

    def __init__(self, content=b"RIFFtest"):
        self.content = content

    def getvalue(self):
        return self.content


class VoicePipelineTests(unittest.TestCase):
    @patch("gnani_service._api_key", return_value="secret-not-printed")
    @patch("gnani_service.requests.post")
    def test_successful_stt_enters_conversation(self, post, _key):
        response = Mock(ok=True)
        response.json.return_value = {"success": True, "transcript": "My tomato leaves are yellow"}
        post.return_value = response
        result = gnani_service.transcribe_audio(FakeAudio(), "English")
        self.assertEqual(result.text, "My tomato leaves are yellow")
        turn = process_turn(new_conversation(), result.text)
        self.assertTrue(turn["response"]["reported_observations"])

    @patch("gnani_service._api_key", return_value="configured")
    @patch("gnani_service.requests.post")
    def test_empty_transcript_is_not_processed(self, post, _key):
        response = Mock(ok=True)
        response.json.return_value = {"success": True, "transcript": "   "}
        post.return_value = response
        result = gnani_service.transcribe_audio(FakeAudio(), "English")
        self.assertIsNone(result.text)
        self.assertIn("No speech", result.error)

    @patch("gnani_service._api_key", return_value="configured")
    @patch("gnani_service.requests.post")
    def test_stt_timeout_is_farmer_safe(self, post, _key):
        import requests
        post.side_effect = requests.Timeout()
        result = gnani_service.transcribe_audio(FakeAudio(), "ಕನ್ನಡ (Kannada)")
        self.assertIn("timed out", result.error)

    @patch("gnani_service._api_key", return_value="configured")
    @patch("gnani_service.requests.post")
    def test_tts_success_returns_audio_without_logging_headers(self, post, _key):
        response = Mock(ok=True, status_code=200, content=b"RIFF\x00\x00\x00\x00WAVEfmt ")
        response.headers = {"Content-Type": "audio/wav"}
        post.return_value = response
        result = gnani_service.synthesize_speech("ನಮಸ್ಕಾರ", "ಕನ್ನಡ (Kannada)")
        self.assertEqual(result.audio, b"RIFF\x00\x00\x00\x00WAVEfmt ")
        self.assertEqual(result.content_type, "audio/wav")
        sent_headers = post.call_args.kwargs["headers"]
        self.assertNotIn("secret-not-printed", str(sent_headers))

    @patch("gnani_service._api_key", return_value="configured")
    @patch("gnani_service.requests.post")
    def test_tts_empty_text_does_not_call_api(self, post, _key):
        result = gnani_service.synthesize_speech("", "ಕನ್ನಡ (Kannada)")
        self.assertIsNone(result.audio)
        post.assert_not_called()

    @patch("gnani_service._api_key", return_value="configured")
    @patch("gnani_service.requests.post")
    def test_tts_failure_keeps_error_safe(self, post, _key):
        response = Mock(ok=False, status_code=500, content=b"")
        response.headers = {"Content-Type": "text/plain"}
        response.text = "internal error"
        post.return_value = response
        result = gnani_service.synthesize_speech("A safe response", "English")
        self.assertIsNone(result.audio)
        self.assertIn("temporarily unavailable", result.error)

    @patch("gnani_service._api_key", return_value="configured")
    @patch("gnani_service.requests.post")
    def test_tts_invalid_audio_payload_is_rejected(self, post, _key):
        response = Mock(ok=True, status_code=200, content=b"not audio")
        response.headers = {"Content-Type": "audio/wav"}
        post.return_value = response
        result = gnani_service.synthesize_speech("A response", "English")
        self.assertIsNone(result.audio)
        self.assertIn("invalid audio", result.error)

    @patch("gnani_service._api_key", return_value="configured")
    @patch("gnani_service.requests.post")
    def test_stt_authentication_failure_is_safe(self, post, _key):
        response = Mock(ok=False, status_code=401)
        post.return_value = response
        result = gnani_service.transcribe_audio(FakeAudio(), "English")
        self.assertIn("authentication failed", result.error)
        self.assertNotIn("configured", result.error)

    @patch("gnani_service._api_key", return_value="configured")
    @patch("gnani_service.requests.post")
    def test_stt_malformed_response_is_rejected(self, post, _key):
        response = Mock(ok=True)
        response.json.side_effect = ValueError("bad json")
        post.return_value = response
        result = gnani_service.transcribe_audio(FakeAudio(), "English")
        self.assertIn("invalid response", result.error)

    def test_unsupported_audio_does_not_call_service(self):
        result = gnani_service.transcribe_audio(type("File", (), {"name": "bad.exe", "getvalue": lambda self: b"x"})(), "English")
        self.assertIn("Unsupported audio", result.error)

    def test_voice_text_switch_preserves_same_state(self):
        state = new_conversation()
        first = process_turn(state, "My tomato leaves are yellow")
        second = process_turn(state, "Mostly older leaves")
        self.assertEqual(state.turn_number, 2)
        self.assertEqual(len(state.messages), 4)
        self.assertIsNotNone(first["response"])
        self.assertIsNotNone(second["response"])


if __name__ == "__main__":
    unittest.main()
