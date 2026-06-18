import logging

logger = logging.getLogger(__name__)

DEFAULT_SPOT_MAKER_FEE = 0.001
DEFAULT_SPOT_TAKER_FEE = 0.001
DEFAULT_FUTURES_MAKER_FEE = 0.0004
DEFAULT_FUTURES_TAKER_FEE = 0.0004


def calculate_spot_fee(
    price: float,
    quantity: float,
    is_maker: bool = False,
    maker_fee: float | None = None,
    taker_fee: float | None = None,
) -> dict:
    m_fee = maker_fee if maker_fee is not None else DEFAULT_SPOT_MAKER_FEE
    t_fee = taker_fee if taker_fee is not None else DEFAULT_SPOT_TAKER_FEE
    fee_rate = m_fee if is_maker else t_fee
    notional = price * quantity
    fee_amount = notional * fee_rate
    return {
        "notional": notional,
        "fee_rate": fee_rate,
        "fee_amount": fee_amount,
        "effective_price": price + (fee_amount / quantity) if not is_maker else price - (fee_amount / quantity),
        "fee_type": "maker" if is_maker else "taker",
    }


def calculate_futures_fee(
    price: float,
    quantity: float,
    leverage: int = 1,
    is_maker: bool = False,
    maker_fee: float | None = None,
    taker_fee: float | None = None,
) -> dict:
    m_fee = maker_fee if maker_fee is not None else DEFAULT_FUTURES_MAKER_FEE
    t_fee = taker_fee if taker_fee is not None else DEFAULT_FUTURES_TAKER_FEE
    fee_rate = m_fee if is_maker else t_fee
    notional = price * quantity
    margin = notional / leverage
    fee_amount = notional * fee_rate
    return {
        "notional": notional,
        "margin": margin,
        "leverage": leverage,
        "fee_rate": fee_rate,
        "fee_amount": fee_amount,
        "fee_type": "maker" if is_maker else "taker",
    }


def compare_spot_vs_futures(
    price: float,
    quantity: float,
    leverage: int = 1,
) -> dict:
    spot = calculate_spot_fee(price, quantity, is_maker=False)
    futures = calculate_futures_fee(price, quantity, leverage, is_maker=False)
    fee_diff = spot["fee_amount"] - futures["fee_amount"]
    return {
        "spot": spot,
        "futures": futures,
        "fee_difference": fee_diff,
        "cheaper": "futures" if fee_diff > 0 else "spot",
        "savings_pct": abs(fee_diff) / max(spot["fee_amount"], futures["fee_amount"]) * 100,
    }
