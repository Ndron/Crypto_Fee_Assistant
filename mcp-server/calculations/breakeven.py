import logging

logger = logging.getLogger(__name__)


def calculate_breakeven_move(
    entry_price: float,
    fee_rate: float = 0.001,
    is_futures: bool = False,
    leverage: int = 1,
    side: str = "long",
) -> dict:
    if is_futures:
        effective_fee_rate = fee_rate * leverage
    else:
        effective_fee_rate = fee_rate * 2

    breakeven_pct = effective_fee_rate * 100

    if side.lower() == "long":
        breakeven_price = entry_price * (1 + effective_fee_rate)
    else:
        breakeven_price = entry_price * (1 - effective_fee_rate)

    price_move = abs(breakeven_price - entry_price)

    return {
        "entry_price": entry_price,
        "breakeven_price": round(breakeven_price, 8),
        "price_move": round(price_move, 8),
        "breakeven_pct": round(breakeven_pct, 4),
        "fee_rate": fee_rate,
        "is_futures": is_futures,
        "leverage": leverage,
        "side": side,
        "note": f"Price must move {breakeven_pct:.4f}% {'up' if side == 'long' else 'down'} to cover fees",
    }


def calculate_breakeven_with_slippage(
    entry_price: float,
    fee_rate: float = 0.001,
    slippage_pct: float = 0.05,
    is_futures: bool = False,
    leverage: int = 1,
    side: str = "long",
) -> dict:
    base = calculate_breakeven_move(entry_price, fee_rate, is_futures, leverage, side)

    slippage_amount = entry_price * (slippage_pct / 100)

    if side.lower() == "long":
        total_breakeven_price = base["breakeven_price"] + slippage_amount
    else:
        total_breakeven_price = base["breakeven_price"] - slippage_amount

    total_move = abs(total_breakeven_price - entry_price)
    total_pct = (total_move / entry_price) * 100

    return {
        **base,
        "slippage_pct": slippage_pct,
        "slippage_amount": round(slippage_amount, 8),
        "total_breakeven_price": round(total_breakeven_price, 8),
        "total_move": round(total_move, 8),
        "total_breakeven_pct": round(total_pct, 4),
    }
