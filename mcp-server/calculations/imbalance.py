import logging

logger = logging.getLogger(__name__)


def calculate_order_book_imbalance(
    bids: list[list[str | float]],
    asks: list[list[str | float]],
    levels: int = 20,
) -> dict:
    bid_levels = bids[:levels]
    ask_levels = asks[:levels]

    bid_volume = sum(float(b[1]) for b in bid_levels)
    ask_volume = sum(float(a[1]) for a in ask_levels)

    total_volume = bid_volume + ask_volume
    if total_volume == 0:
        return {"error": "No volume in order book"}

    imbalance_ratio = (bid_volume - ask_volume) / total_volume
    bid_pct = (bid_volume / total_volume) * 100
    ask_pct = (ask_volume / total_volume) * 100

    if imbalance_ratio > 0.3:
        signal = "strong_buy_pressure"
    elif imbalance_ratio > 0.1:
        signal = "moderate_buy_pressure"
    elif imbalance_ratio < -0.3:
        signal = "strong_sell_pressure"
    elif imbalance_ratio < -0.1:
        signal = "moderate_sell_pressure"
    else:
        signal = "neutral"

    best_bid = float(bid_levels[0][0]) if bid_levels else 0
    best_ask = float(ask_levels[0][0]) if ask_levels else 0
    spread = best_ask - best_bid
    spread_pct = (spread / best_ask * 100) if best_ask else 0

    bid_depth = sum(float(b[0]) * float(b[1]) for b in bid_levels)
    ask_depth = sum(float(a[0]) * float(a[1]) for a in ask_levels)

    return {
        "imbalance_ratio": round(imbalance_ratio, 4),
        "bid_volume": round(bid_volume, 4),
        "ask_volume": round(ask_volume, 4),
        "bid_pct": round(bid_pct, 2),
        "ask_pct": round(ask_pct, 2),
        "signal": signal,
        "spread": round(spread, 8),
        "spread_pct": round(spread_pct, 4),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "bid_depth_usd": round(bid_depth, 2),
        "ask_depth_usd": round(ask_depth, 2),
        "levels_analyzed": levels,
    }


def calculate_wall_detection(
    bids: list[list[str | float]],
    asks: list[list[str | float]],
    wall_threshold_pct: float = 5.0,
) -> dict:
    bid_levels = [(float(b[0]), float(b[1])) for b in bids[:50]]
    ask_levels = [(float(a[0]), float(a[1])) for a in asks[:50]]

    total_bid_vol = sum(v for _, v in bid_levels)
    total_ask_vol = sum(v for _, v in ask_levels)

    bid_walls = []
    for price, volume in bid_levels:
        pct = (volume / total_bid_vol * 100) if total_bid_vol else 0
        if pct >= wall_threshold_pct:
            bid_walls.append({"price": price, "volume": volume, "pct_of_total": round(pct, 2)})

    ask_walls = []
    for price, volume in ask_levels:
        pct = (volume / total_ask_vol * 100) if total_ask_vol else 0
        if pct >= wall_threshold_pct:
            ask_walls.append({"price": price, "volume": volume, "pct_of_total": round(pct, 2)})

    return {
        "bid_walls": bid_walls[:5],
        "ask_walls": ask_walls[:5],
        "wall_threshold_pct": wall_threshold_pct,
        "total_bid_volume": round(total_bid_vol, 4),
        "total_ask_volume": round(total_ask_vol, 4),
    }
