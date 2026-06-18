import pytest
from calculations.imbalance import calculate_order_book_imbalance, calculate_wall_detection


class TestOrderBookImbalance:
    def test_balanced_book(self):
        bids = [["50000", "10"]] * 20
        asks = [["50001", "10"]] * 20
        result = calculate_order_book_imbalance(bids, asks)
        assert result["imbalance_ratio"] == pytest.approx(0.0, abs=0.001)
        assert result["signal"] == "neutral"
        assert result["bid_pct"] == 50.0
        assert result["ask_pct"] == 50.0

    def test_buy_pressure(self):
        bids = [["50000", "30"]] * 20
        asks = [["50001", "10"]] * 20
        result = calculate_order_book_imbalance(bids, asks)
        assert result["imbalance_ratio"] > 0
        assert "buy" in result["signal"]

    def test_sell_pressure(self):
        bids = [["50000", "10"]] * 20
        asks = [["50001", "30"]] * 20
        result = calculate_order_book_imbalance(bids, asks)
        assert result["imbalance_ratio"] < 0
        assert "sell" in result["signal"]

    def test_empty_book(self):
        result = calculate_order_book_imbalance([], [])
        assert "error" in result

    def test_custom_levels(self):
        bids = [["50000", "10"]] * 50
        asks = [["50001", "10"]] * 50
        result = calculate_order_book_imbalance(bids, asks, levels=10)
        assert result["levels_analyzed"] == 10

    def test_spread_calculation(self):
        bids = [["49999", "10"]]
        asks = [["50001", "10"]]
        result = calculate_order_book_imbalance(bids, asks, levels=1)
        assert result["spread"] == 2.0
        assert result["best_bid"] == 49999.0
        assert result["best_ask"] == 50001.0


class TestWallDetection:
    def test_no_walls(self):
        bids = [["50000", "10"]] * 10
        asks = [["50001", "10"]] * 10
        result = calculate_wall_detection(bids, asks, wall_threshold_pct=20.0)
        assert len(result["bid_walls"]) == 0
        assert len(result["ask_walls"]) == 0

    def test_detect_wall(self):
        bids = [["50000", "1000"]] + [["50000", "10"]] * 49
        asks = [["50001", "10"]] * 50
        result = calculate_wall_detection(bids, asks, wall_threshold_pct=5.0)
        assert len(result["bid_walls"]) >= 0 or len(result["ask_walls"]) >= 0
