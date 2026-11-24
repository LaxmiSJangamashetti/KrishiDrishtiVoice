"""Server-side AgroMonitoring weather access with safe error handling."""
from __future__ import annotations

import os
import time
from functools import lru_cache
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://api.agromonitoring.com/agro/1.0"


class AgroMonitoringError(RuntimeError):
    def __init__(self, message: str, *, category: str = "service_error", diagnostic: dict[str, Any] | None = None):
        super().__init__(message)
        self.category = category
        self.diagnostic = diagnostic or {}


def _key() -> str:
    key = os.getenv("AGROMONITORING_API_KEY", "").strip()
    if not key:
        raise AgroMonitoringError("AgroMonitoring is not configured.")
    return key


def _validate_coordinates(lat: float, lon: float) -> tuple[float, float]:
    try:
        lat_value, lon_value = float(lat), float(lon)
    except (TypeError, ValueError) as exc:
        raise AgroMonitoringError("Saved farm coordinates are invalid.", category="invalid_coordinates") from exc
    if not (-90 <= lat_value <= 90 and -180 <= lon_value <= 180) or (lat_value == 0 and lon_value == 0):
        raise AgroMonitoringError("Saved farm coordinates are invalid.", category="invalid_coordinates")
    return lat_value, lon_value


def _safe_error(response: requests.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            value = payload.get("message") or payload.get("error") or payload.get("cod")
            if value is not None:
                return str(value)[:240]
    except ValueError:
        pass
    return response.text[:240].replace("\n", " ")


@lru_cache(maxsize=32)
def _get_cached(path: str, lat: float, lon: float) -> dict[str, Any] | list[Any]:
    started = time.monotonic()
    try:
        lat, lon = _validate_coordinates(lat, lon)
        response = requests.get(f"{BASE_URL}/{path}", params={"lat": lat, "lon": lon, "appid": _key()}, timeout=(5, 15))
        if response.status_code in (401, 403):
            category = "subscription_restriction" if response.status_code == 403 else "authentication_failure"
            raise AgroMonitoringError("AgroMonitoring authorization failed; check the account plan or API key.", category=category, diagnostic={"status": response.status_code, "body": _safe_error(response)})
        if response.status_code == 429:
            raise AgroMonitoringError("AgroMonitoring rate limit reached. Try again later.", category="rate_limit", diagnostic={"status": 429})
        if response.status_code >= 400:
            raise AgroMonitoringError(f"AgroMonitoring returned HTTP {response.status_code}.", category="http_error", diagnostic={"status": response.status_code, "body": _safe_error(response)})
        payload = response.json()
        if path == "weather" and not isinstance(payload, dict):
            raise AgroMonitoringError("AgroMonitoring current-weather response was not an object.", category="unexpected_structure", diagnostic={"json_type": type(payload).__name__})
        if path == "weather/forecast" and not isinstance(payload, list):
            raise AgroMonitoringError("AgroMonitoring forecast response was not an array.", category="unexpected_structure", diagnostic={"json_type": type(payload).__name__})
        return payload
    except AgroMonitoringError:
        raise
    except requests.Timeout as exc:
        raise AgroMonitoringError("AgroMonitoring timed out.", category="timeout") from exc
    except requests.RequestException as exc:
        raise AgroMonitoringError("AgroMonitoring could not be reached.", category="network_failure") from exc
    except ValueError as exc:
        raise AgroMonitoringError("AgroMonitoring returned invalid JSON.", category="invalid_json") from exc


def current_weather(*, lat: float, lon: float) -> dict[str, Any]:
    return _get_cached("weather", float(lat), float(lon))


def weather_forecast(*, lat: float, lon: float) -> list[Any]:
    return _get_cached("weather/forecast", float(lat), float(lon))


def clear_cache() -> None:
    _get_cached.cache_clear()


def temperature_celsius(value: Any) -> float | None:
    """Convert the documented default Kelvin response exactly once for display."""
    try:
        return round(float(value) - 273.15, 1)
    except (TypeError, ValueError):
        return None
