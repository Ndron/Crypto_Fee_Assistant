import logging
from typing import Any

import httpx

from config import BINANCE_BASE_URL, BINANCE_FUTURES_URL, BINANCE_API_KEY
from utils import cached, rate_limit

logger = logging.getLogger(__name__)


def _get(url: str, params: dict | None = None, base_url: str | None = None) -> dict:
    full_url = f"{base_url or BINANCE_BASE_URL}{url}"
    headers = {}
    if BINANCE_API_KEY:
        headers["X-MBX-APIKEY"] = BINANCE_API_KEY
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(full_url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Binance API error: {e.response.status_code} {e.response.text}")
        return {"error": f"API error: {e.response.status_code}", "detail": e.response.text}
    except httpx.RequestError as e:
        logger.error(f"Binance request error: {e}")
        return {"error": f"Request failed: {str(e)}"}


@rate_limit(max_calls=10, period=1)
@cached(ttl=60)
def get_spot_price(symbol: str) -> dict:
    return _get("/api/v3/ticker/price", {"symbol": symbol.upper()})


@rate_limit(max_calls=10, period=1)
@cached(ttl=60)
def get_futures_price(symbol: str) -> dict:
    return _get("/fapi/v1/ticker/price", {"symbol": symbol.upper()}, BINANCE_FUTURES_URL)


@rate_limit(max_calls=5, period=1)
@cached(ttl=300)
def get_exchange_info() -> dict:
    return _get("/api/v3/exchangeInfo")


@rate_limit(max_calls=5, period=1)
@cached(ttl=300)
def get_futures_exchange_info() -> dict:
    return _get("/fapi/v1/exchangeInfo", base_url=BINANCE_FUTURES_URL)


@rate_limit(max_calls=5, period=1)
@cached(ttl=60)
def get_spot_fee(symbol: str) -> dict:
    result = _get("/api/v3/exchangeInfo")
    if "error" in result:
        return result
    for s in result.get("symbols", []):
        if s["symbol"] == symbol.upper():
            return {
                "symbol": s["symbol"],
                "baseCommission": s.get("baseCommission", "0.001"),
                "quoteCommission": s.get("quoteCommission", "0.001"),
                "icebergAllowed": s.get("icebergAllowed", False),
                "ocoAllowed": s.get("ocoAllowed", False),
                "orderTypes": s.get("orderTypes", []),
            }
    return {"error": f"Symbol {symbol} not found"}


@rate_limit(max_calls=5, period=1)
@cached(ttl=60)
def get_futures_fee(symbol: str) -> dict:
    result = _get("/fapi/v1/exchangeInfo", base_url=BINANCE_FUTURES_URL)
    if "error" in result:
        return result
    for s in result.get("symbols", []):
        if s["symbol"] == symbol.upper():
            return {
                "symbol": s["symbol"],
                "pricePrecision": s.get("pricePrecision"),
                "quantityPrecision": s.get("quantityPrecision"),
                "orderTypes": s.get("orderTypes", []),
            }
    return {"error": f"Symbol {symbol} not found in futures"}


@rate_limit(max_calls=10, period=1)
@cached(ttl=30)
def get_order_book(symbol: str, limit: int = 20) -> dict:
    return _get("/api/v3/depth", {"symbol": symbol.upper(), "limit": min(limit, 100)})


@rate_limit(max_calls=10, period=1)
@cached(ttl=30)
def get_futures_order_book(symbol: str, limit: int = 20) -> dict:
    return _get("/fapi/v1/depth", {"symbol": symbol.upper(), "limit": min(limit, 100)}, BINANCE_FUTURES_URL)


@rate_limit(max_calls=10, period=1)
@cached(ttl=120)
def get_funding_rate(symbol: str) -> dict:
    return _get("/fapi/v1/fundingRate", {"symbol": symbol.upper(), "limit": 1}, BINANCE_FUTURES_URL)


@rate_limit(max_calls=5, period=1)
@cached(ttl=120)
def get_funding_history(symbol: str, limit: int = 10) -> dict:
    return _get("/fapi/v1/fundingRate", {"symbol": symbol.upper(), "limit": min(limit, 100)}, BINANCE_FUTURES_URL)


@rate_limit(max_calls=10, period=1)
@cached(ttl=30)
def get_ticker_24h(symbol: str) -> dict:
    return _get("/api/v3/ticker/24hr", {"symbol": symbol.upper()})


@rate_limit(max_calls=10, period=1)
@cached(ttl=60)
def get_futures_ticker_24h(symbol: str) -> dict:
    return _get("/fapi/v1/ticker/24hr", {"symbol": symbol.upper()}, BINANCE_FUTURES_URL)


@rate_limit(max_calls=10, period=1)
@cached(ttl=30)
def get_klines(symbol: str, interval: str = "1h", limit: int = 100, is_futures: bool = False) -> dict:
    base = BINANCE_FUTURES_URL if is_futures else BINANCE_BASE_URL
    endpoint = "/fapi/v1/klines" if is_futures else "/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": min(limit, 500),
    }
    raw = _get(endpoint, params, base)
    if "error" in raw:
        return raw

    candles = []
    for k in raw:
        candles.append({
            "time": k[0] // 1000,
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
        })
    return {
        "symbol": symbol.upper(),
        "interval": interval,
        "is_futures": is_futures,
        "count": len(candles),
        "candles": candles,
    }
