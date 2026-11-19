import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import dotenv_values

API_URL = "https://api.vachana.ai/stt/v3"
TTS_API_URL = "https://api.vachana.ai/api/v1/tts/inference"
ENV_PATH = Path(__file__).resolve().parent / ".env"
LANGUAGE_CODES = {"English": "en-IN", "ಕನ್ನಡ (Kannada)": "kn-IN"}
# The current Gnani Timbre v2.5 reference lists these BCP-47 locales and
# catalog voices. Per-account/per-locale availability still requires live verification.
TTS_LANGUAGE_CODES = {
    "ಕನ್ನಡ (Kannada)": "kn-IN",
    "English": "en-IN",
    "Hindi": "hi-IN",
}
TTS_VOICES = {
    "ಕನ್ನಡ (Kannada)": "Nalini",
    "English": "Kaveri",
    "Hindi": "Nalini",
}
SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a"}


@dataclass
class TranscriptionResult:
    text: str | None = None
    error: str | None = None


@dataclass
class SpeechSynthesisResult:
    audio: bytes | None = None
    content_type: str | None = None
    status_code: int | None = None
    error: str | None = None
    diagnostic: dict[str, str | int | None] | None = None


def _api_key() -> str | None:
    values = dotenv_values(ENV_PATH)
    key = values.get("GNANI_API_KEY_ID")
    return key.strip() if isinstance(key, str) and key.strip() else None


def _file_metadata(audio_file: Any) -> tuple[str, str, bytes] | None:
    name = getattr(audio_file, "name", "audio") or "audio"
    if Path(name).suffix.lower() not in SUPPORTED_EXTENSIONS:
        return None
    content = audio_file.getvalue() if hasattr(audio_file, "getvalue") else audio_file.read()
    content_type = getattr(audio_file, "type", None) or mimetypes.guess_type(name)[0] or "application/octet-stream"
    return name, content_type, content


def _error_from_response(response: requests.Response) -> str:
    if response.status_code in (401, 403):
        return "Gnani authentication failed. Check GNANI_API_KEY_ID in .env."
    if response.status_code == 400:
        return "Gnani rejected the audio or request. Check that the file is supported and no longer than 30 seconds."
    if response.status_code == 413:
        return "The audio file is too large for the Prisma REST request."
    if response.status_code == 429:
        return "Gnani rate limit or credit limit reached. Please try again later."
    if response.status_code >= 500:
        return "Gnani is temporarily unavailable. Please try again later."
    return f"Gnani returned an unexpected HTTP error ({response.status_code})."


def _safe_response_diagnostic(response: requests.Response, endpoint: str) -> dict[str, str | int | None]:
    """Return bounded, non-secret details useful for diagnosing API validation errors."""
    body = response.text.strip()
    body = re.sub(
        r"(?i)([\"']?(?:x-api-key-id|authorization|api[_-]?key)[\"']?\s*[:=]\s*)(?:\"[^\"]*\"|'[^']*'|[^,}]+)",
        r"\1[REDACTED]",
        body,
    )
    if len(body) > 800:
        body = body[:800] + "…"
    return {
        "endpoint": endpoint,
        "status_code": response.status_code,
        "content_type": response.headers.get("Content-Type"),
        "body": body or None,
    }


def transcribe_audio(audio_file: Any, language: str, timeout: int = 60) -> TranscriptionResult:
    """Transcribe a short recording with the documented Prisma v2.5 REST API."""
    api_key = _api_key()
    if not api_key:
        return TranscriptionResult(error="Gnani credentials are not configured. Add GNANI_API_KEY_ID to .env.")
    language_code = LANGUAGE_CODES.get(language)
    if not language_code:
        return TranscriptionResult(error="Unsupported language selection.")
    metadata = _file_metadata(audio_file)
    if metadata is None:
        return TranscriptionResult(error="Unsupported audio format. Use WAV, MP3, OGG, FLAC, AAC, or M4A.")
    filename, content_type, content = metadata
    if not content:
        return TranscriptionResult(error="The selected audio file is empty.")
    try:
        response = requests.post(API_URL, headers={"X-API-Key-ID": api_key}, files={"audio_file": (filename, content, content_type)}, data={"language_code": language_code, "format": "verbatim"}, timeout=timeout)
    except requests.Timeout:
        return TranscriptionResult(error="The Gnani request timed out. Check your connection and try again.")
    except requests.RequestException:
        return TranscriptionResult(error="Could not reach Gnani. Check your network connection and try again.")
    if not response.ok:
        return TranscriptionResult(error=_error_from_response(response))
    try:
        body = response.json()
    except ValueError:
        return TranscriptionResult(error="Gnani returned an invalid response.")
    if body.get("success") is not True:
        return TranscriptionResult(error="Gnani could not transcribe this audio request.")
    transcript = body.get("transcript")
    if not isinstance(transcript, str):
        return TranscriptionResult(error="Gnani returned no usable transcript.")
    if not transcript.strip():
        return TranscriptionResult(error="No speech was detected in the audio.")
    return TranscriptionResult(text=str(transcript).strip())


def synthesize_speech(text: str, language: str, timeout: int = 60) -> SpeechSynthesisResult:
    """Synthesize a safe, validated agricultural response with Gnani Timbre v2.5."""
    api_key = _api_key()
    if not api_key:
        return SpeechSynthesisResult(error="Gnani credentials are not configured. Add GNANI_API_KEY_ID to .env.")
    language_code = TTS_LANGUAGE_CODES.get(language)
    voice = TTS_VOICES.get(language)
    if not language_code or not voice:
        return SpeechSynthesisResult(error="TTS is not enabled for this language.")
    if not isinstance(text, str) or not text.strip():
        return SpeechSynthesisResult(error="There is no response text to synthesize.")
    payload = {
        "text": text.strip(),
        "voice": voice,
        "model": "timbre-v2.5",
        "language": language_code,
        "speed": 1,
        "audio_config": {
            "encoding": "linear_pcm",
            "container": "wav",
            "num_channels": 1,
            "sample_rate": 48000,
            "sample_width": 2,
        },
    }
    try:
        response = requests.post(
            TTS_API_URL,
            headers={"X-API-Key-ID": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
    except requests.Timeout:
        return SpeechSynthesisResult(error="Gnani Timbre request timed out. Check your connection and try again.")
    except requests.RequestException:
        return SpeechSynthesisResult(error="Could not reach Gnani Timbre. Check your network connection and try again.")
    if not response.ok:
        if response.status_code in (401, 403):
            message = "Gnani TTS authentication failed. Confirm the existing key has TTS scope."
        elif response.status_code == 429:
            message = "Gnani TTS rate or credit limit reached."
        elif response.status_code >= 500:
            message = "Gnani Timbre is temporarily unavailable."
        else:
            message = f"Gnani Timbre returned HTTP {response.status_code}."
        diagnostic = _safe_response_diagnostic(response, TTS_API_URL)
        detail = diagnostic.get("body")
        if detail:
            message = f"{message} Server response: {detail}"
        return SpeechSynthesisResult(status_code=response.status_code, error=message, diagnostic=diagnostic)
    audio = response.content
    if not audio:
        return SpeechSynthesisResult(status_code=response.status_code, error="Gnani Timbre returned an empty audio response.")
    return SpeechSynthesisResult(audio=audio, content_type=response.headers.get("Content-Type", "audio/wav"), status_code=response.status_code)


def save_transcript(transcript: str, destination: Path) -> None:
    """Persist the exact returned Unicode transcript as UTF-8."""
    destination.write_text(transcript, encoding="utf-8", newline="")
