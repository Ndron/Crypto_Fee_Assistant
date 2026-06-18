import pytest
from calculations.breakeven import calculate_breakeven_move, calculate_breakeven_with_slippage


class TestBreakevenMove:
    def test_spot_long(self):
        result = calculate_breakeven_move(50000.0, fee_rate=0.001, side="long")
        assert result["entry_price"] == 50000.0
        assert result["breakeven_price"] > 50000.0
        assert result["breakeven_pct"] == pytest.approx(0.2, abs=0.01)
        assert result["side"] == "long"

    def test_spot_short(self):
        result = calculate_breakeven_move(50000.0, fee_rate=0.001, side="short")
        assert result["breakeven_price"] < 50000.0
        assert result["side"] == "short"

    def test_futures_with_leverage(self):
        result = calculate_breakeven_move(50000.0, fee_rate=0.0004, is_futures=True, leverage=10, side="long")
        assert result["leverage"] == 10
        assert result["is_futures"] == True
        assert result["breakeven_pct"] == pytest.approx(0.4, abs=0.01)

    def test_zero_fee(self):
        result = calculate_breakeven_move(50000.0, fee_rate=0.0, side="long")
        assert result["breakeven_price"] == 50000.0
        assert result["breakeven_pct"] == 0.0


class TestBreakevenWithSlippage:
    def test_with_slippage_long(self):
        result = calculate_breakeven_with_slippage(50000.0, fee_rate=0.001, slippage_pct=0.05, side="long")
        base = calculate_breakeven_move(50000.0, fee_rate=0.001, side="long")
        assert result["total_breakeven_price"] > base["breakeven_price"]
        assert result["slippage_pct"] == 0.05

    def test_with_slippage_short(self):
        result = calculate_breakeven_with_slippage(50000.0, fee_rate=0.001, slippage_pct=0.05, side="short")
        base = calculate_breakeven_move(50000.0, fee_rate=0.001, side="short")
        assert result["total_breakeven_price"] < base["breakeven_price"]
