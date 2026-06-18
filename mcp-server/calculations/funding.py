import logging
from typing import Any

logger = logging.getLogger(__name__)


def analyze_funding_opportunity(
    funding_rate: float,
    mark_price: float,
    index_price: float,
    annualize: bool = True,
) -> dict:
    rate_pct = funding_rate * 100
    estimated_annual = rate_pct * 3 * 365 if annualize else None

    if funding_rate > 0:
        side = "short"
        description = "Positive funding: shorts receive, longs pay"
        opportunity = "Consider short position to earn funding"
    elif funding_rate < 0:
        side = "long"
        description = "Negative funding: longs receive, shorts pay"
        opportunity = "Consider long position to earn funding"
    else:
        side = "neutral"
        description = "Neutral funding rate"
        opportunity = "No funding advantage"

    premium = ((mark_price - index_price) / index_price) * 100 if index_price else 0

    return {
        "funding_rate": funding_rate,
        "funding_rate_pct": round(rate_pct, 6),
        "estimated_annual_pct": round(estimated_annual, 2) if estimated_annual else None,
        "favored_side": side,
        "description": description,
        "opportunity": opportunity,
        "mark_price": mark_price,
        "index_price": index_price,
        "basis_premium_pct": round(premium, 4),
    }


def compare_funding_rates(rates: list[dict]) -> dict:
    if not rates:
        return {"error": "No funding rates provided"}

    sorted_rates = sorted(rates, key=lambda x: x.get("funding_rate", 0), reverse=True)

    best_long = sorted_rates[-1] if sorted_rates else None
    best_short = sorted_rates[0] if sorted_rates else None

    return {
        "highest_funding": best_short,
        "lowest_funding": best_long,
        "rates": sorted_rates,
    }
