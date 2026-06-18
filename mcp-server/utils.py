import time
import logging
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger(__name__)

_cache: dict[str, tuple[Any, float]] = {}
_rate_limit: dict[str, list[float]] = {}


def cached(ttl: int = 60):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            now = time.time()
            if cache_key in _cache:
                value, ts = _cache[cache_key]
                if now - ts < ttl:
                    logger.debug(f"Cache hit for {cache_key}")
                    return value
            result = func(*args, **kwargs)
            _cache[cache_key] = (result, now)
            return result
        return wrapper
    return decorator


def rate_limit(max_calls: int = 10, period: int = 1):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = func.__name__
            now = time.time()
            if key not in _rate_limit:
                _rate_limit[key] = []
            _rate_limit[key] = [t for t in _rate_limit[key] if now - t < period]
            if len(_rate_limit[key]) >= max_calls:
                logger.warning(f"Rate limit hit for {key}")
                return {"error": f"Rate limit exceeded for {key}. Try again in {period}s."}
            _rate_limit[key].append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
