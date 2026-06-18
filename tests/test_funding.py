import pytest
from calculations.funding import analyze_funding_opportunity, compare_funding_rates


class TestFundingOpportunity:
    def test_positive_funding(self):
        result = analyze_funding_opportunity(0.0001, 50000.0, 49999.0)
        assert result["favored_side"] == "short"
        assert result["funding_rate_pct"] == pytest.approx(0.01, abs=0.001)
        assert "earn funding" in result["opportunity"].lower() or "short" in result["opportunity"].lower()

    def test_negative_funding(self):
        result = analyze_funding_opportunity(-0.0001, 50000.0, 50001.0)
        assert result["favored_side"] == "long"

    def test_zero_funding(self):
        result = analyze_funding_opportunity(0.0, 50000.0, 50000.0)
        assert result["favored_side"] == "neutral"

    def test_annualized(self):
        result = analyze_funding_opportunity(0.0001, 50000.0, 49999.0, annualize=True)
        assert result["estimated_annual_pct"] is not None
        expected = 0.01 * 3 * 365
        assert result["estimated_annual_pct"] == pytest.approx(expected, abs=0.1)

    def test_basis_premium(self):
        result = analyze_funding_opportunity(0.0001, 50100.0, 50000.0)
        assert result["basis_premium_pct"] == pytest.approx(0.2, abs=0.01)


class TestCompareFundingRates:
    def test_compare(self):
        rates = [
            {"symbol": "BTCUSDT", "funding_rate": 0.0001},
            {"symbol": "ETHUSDT", "funding_rate": -0.0002},
            {"symbol": "SOLUSDT", "funding_rate": 0.0003},
        ]
        result = compare_funding_rates(rates)
        assert result["highest_funding"]["symbol"] == "SOLUSDT"
        assert result["lowest_funding"]["symbol"] == "ETHUSDT"

    def test_empty_rates(self):
        result = compare_funding_rates([])
        assert "error" in result
