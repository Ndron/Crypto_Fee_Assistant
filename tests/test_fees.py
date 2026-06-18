import pytest
from calculations.fees import (
    calculate_spot_fee,
    calculate_futures_fee,
    compare_spot_vs_futures,
)


class TestSpotFee:
    def test_taker_fee(self):
        result = calculate_spot_fee(50000.0, 0.1, is_maker=False)
        assert result["notional"] == 5000.0
        assert result["fee_rate"] == 0.001
        assert result["fee_amount"] == 5.0
        assert result["fee_type"] == "taker"

    def test_maker_fee(self):
        result = calculate_spot_fee(50000.0, 0.1, is_maker=True)
        assert result["fee_rate"] == 0.001
        assert result["fee_type"] == "maker"

    def test_custom_fee(self):
        result = calculate_spot_fee(50000.0, 0.1, is_maker=False, taker_fee=0.002)
        assert result["fee_rate"] == 0.002
        assert result["fee_amount"] == 10.0


class TestFuturesFee:
    def test_taker_fee_with_leverage(self):
        result = calculate_futures_fee(50000.0, 0.1, leverage=10, is_maker=False)
        assert result["notional"] == 5000.0
        assert result["margin"] == 500.0
        assert result["leverage"] == 10
        assert result["fee_rate"] == 0.0004
        assert result["fee_amount"] == 2.0

    def test_maker_fee(self):
        result = calculate_futures_fee(50000.0, 0.1, is_maker=True)
        assert result["fee_type"] == "maker"
        assert result["fee_rate"] == 0.0004


class TestCompareSpotFutures:
    def test_futures_cheaper(self):
        result = compare_spot_vs_futures(50000.0, 0.1)
        assert result["cheaper"] == "futures"
        assert result["fee_difference"] > 0
