"""Mandi Price API client based only on the supplied owner specification."""
from __future__ import annotations

from datetime import date
from typing import Any
from functools import lru_cache

import requests

BASE_URL = "https://mandi-api.onrender.com/v1"
SUPPORTED_STATES = {"Maharashtra", "Uttar Pradesh", "Punjab", "Madhya Pradesh", "Karnataka"}


class MarketServiceError(RuntimeError):
    pass


@lru_cache(maxsize=64)
def _get_cached(path: str, query: tuple[tuple[str, str], ...]) -> dict[str, Any]:
    try:
        response = requests.get(f"{BASE_URL}/{path.lstrip('/')}", params=dict(query), timeout=(5, 20))
        if response.status_code == 429:
            raise MarketServiceError("The market service rate limit was reached. Try again later.")
        if response.status_code >= 400:
            raise MarketServiceError(f"The market service returned HTTP {response.status_code}.")
        payload = response.json()
        if not isinstance(payload, dict) or payload.get("success") is False:
            raise MarketServiceError("The market service returned an unsuccessful response.")
        if "data" not in payload:
            raise MarketServiceError("The market service response is missing data.")
        return payload
    except MarketServiceError:
        raise
    except requests.Timeout as exc:
        raise MarketServiceError("The market service timed out.") from exc
    except requests.RequestException as exc:
        raise MarketServiceError("The market service could not be reached.") from exc
    except ValueError as exc:
        raise MarketServiceError("The market service returned invalid JSON.") from exc


def _get(path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    return _get_cached(path, tuple(sorted((params or {}).items())))


def clear_cache() -> None:
    _get_cached.cache_clear()


def is_market_query(text: str) -> bool:
    lowered = text.casefold()
    return any(term in lowered for term in ("mandi", "price", "market price", "wholesale price", "ಬೆಲೆ", "ಮಾರುಕಟ್ಟೆ"))


def states() -> list[str]:
    return list(_get("states")["data"])


def commodities(*, state: str | None = None, market: str | None = None) -> list[str]:
    params = {k: v for k, v in {"state": state, "market": market}.items() if v}
    return list(_get("commodities", params)["data"])


def markets(*, state: str) -> list[dict[str, Any]]:
    if state not in SUPPORTED_STATES:
        raise MarketServiceError("Unsupported state.")
    return list(_get("markets", {"state": state})["data"])


def prices(*, state: str | None = None, commodity: str | None = None, market: str | None = None, variety: str | None = None, on_date: date | None = None) -> dict[str, Any]:
    if not state and not commodity:
        raise MarketServiceError("Select a state or commodity.")
    params = {k: v for k, v in {"state": state, "commodity": commodity, "market": market, "variety": variety, "date": on_date.isoformat() if on_date else None}.items() if v}
    return _get("prices", params)


def price_history(*, state: str, commodity: str, market: str | None = None, start: date | None = None, end: date | None = None) -> dict[str, Any]:
    params = {k: v for k, v in {"state": state, "commodity": commodity, "market": market, "from": start.isoformat() if start else None, "to": end.isoformat() if end else None}.items() if v}
    return _get("prices/history", params)
