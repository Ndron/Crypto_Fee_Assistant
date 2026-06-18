import os
import logging

logger = logging.getLogger(__name__)

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
BINANCE_FUTURES_URL = os.getenv("BINANCE_FUTURES_URL", "https://fapi.binance.com")
CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))
RATE_LIMIT_CALLS = int(os.getenv("RATE_LIMIT_CALLS", "10"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "1"))
