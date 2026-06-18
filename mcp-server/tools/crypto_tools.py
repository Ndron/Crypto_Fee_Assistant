import json
import logging
import uuid
from typing import Any

from mcp.server.fastmcp import FastMCP

from exchange.binance import (
    get_spot_price,
    get_futures_price,
    get_spot_fee,
    get_futures_fee,
    get_order_book,
    get_futures_order_book,
    get_funding_rate,
    get_funding_history,
    get_ticker_24h,
    get_futures_ticker_24h,
    get_klines,
)
from calculations.fees import calculate_spot_fee, calculate_futures_fee, compare_spot_vs_futures
from calculations.breakeven import calculate_breakeven_move, calculate_breakeven_with_slippage
from calculations.imbalance import calculate_order_book_imbalance, calculate_wall_detection
from calculations.funding import analyze_funding_opportunity, compare_funding_rates

logger = logging.getLogger(__name__)


def register(mcp: FastMCP):

    @mcp.tool()
    def get_spot_price_tool(symbol: str) -> str:
        """Get the current spot price for a trading pair on Binance.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')
        """
        result = get_spot_price(symbol)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_futures_price_tool(symbol: str) -> str:
        """Get the current futures price for a trading pair on Binance.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')
        """
        result = get_futures_price(symbol)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def calculate_trading_fees(
        symbol: str,
        price: float,
        quantity: float,
        is_futures: bool = False,
        leverage: int = 1,
        is_maker: bool = False,
    ) -> str:
        """Calculate trading fees for a given order on Binance.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            price: Order price in quote currency
            quantity: Order quantity in base currency
            is_futures: Whether this is a futures trade (default: False)
            leverage: Leverage for futures (default: 1)
            is_maker: Whether this is a maker order (default: False)
        """
        if is_futures:
            result = calculate_futures_fee(price, quantity, leverage, is_maker)
        else:
            result = calculate_spot_fee(price, quantity, is_maker)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def calculate_breakeven(
        entry_price: float,
        fee_rate: float = 0.001,
        is_futures: bool = False,
        leverage: int = 1,
        side: str = "long",
        include_slippage: bool = False,
        slippage_pct: float = 0.05,
    ) -> str:
        """Calculate the breakeven price move needed to cover trading fees.
        
        Args:
            entry_price: Entry price of the position
            fee_rate: Fee rate (default: 0.001 for 0.1%)
            is_futures: Whether this is a futures trade (default: False)
            leverage: Leverage for futures (default: 1)
            side: Position side - 'long' or 'short' (default: 'long')
            include_slippage: Include slippage in calculation (default: False)
            slippage_pct: Estimated slippage percentage (default: 0.05)
        """
        if include_slippage:
            result = calculate_breakeven_with_slippage(
                entry_price, fee_rate, slippage_pct, is_futures, leverage, side
            )
        else:
            result = calculate_breakeven_move(entry_price, fee_rate, is_futures, leverage, side)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_order_book_imbalance(symbol: str, levels: int = 20, is_futures: bool = False) -> str:
        """Analyze order book imbalance for a trading pair.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            levels: Number of order book levels to analyze (default: 20)
            is_futures: Whether to use futures order book (default: False)
        """
        if is_futures:
            book = get_futures_order_book(symbol, levels)
        else:
            book = get_order_book(symbol, levels)

        if "error" in book:
            return json.dumps(book, indent=2)

        bids = book.get("bids", [])
        asks = book.get("asks", [])
        if not bids or not asks:
            return json.dumps({"error": "Empty order book data"})

        result = calculate_order_book_imbalance(bids, asks, levels)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def detect_order_walls(symbol: str, threshold_pct: float = 5.0) -> str:
        """Detect large order walls in the order book.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            threshold_pct: Minimum percentage of total volume to be considered a wall (default: 5.0)
        """
        book = get_order_book(symbol, 50)
        if "error" in book:
            return json.dumps(book, indent=2)

        bids = book.get("bids", [])
        asks = book.get("asks", [])
        if not bids or not asks:
            return json.dumps({"error": "Empty order book data"})

        result = calculate_wall_detection(bids, asks, threshold_pct)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_funding_rate_info(symbol: str) -> str:
        """Get current funding rate and analyze the funding opportunity.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
        """
        rate_data = get_funding_rate(symbol)
        if "error" in rate_data:
            return json.dumps(rate_data, indent=2)

        if not rate_data or not isinstance(rate_data, list) or len(rate_data) == 0:
            return json.dumps({"error": "No funding rate data available"})

        rate_info = rate_data[0]
        funding_rate = float(rate_info.get("fundingRate", 0))
        mark_price = float(rate_info.get("markPrice", 0))

        result = analyze_funding_opportunity(funding_rate, mark_price, mark_price)
        result["symbol"] = symbol
        result["funding_time"] = rate_info.get("fundingTime")
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_24h_ticker(symbol: str, is_futures: bool = False) -> str:
        """Get 24-hour price change statistics for a trading pair.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            is_futures: Whether to use futures ticker (default: False)
        """
        if is_futures:
            result = get_futures_ticker_24h(symbol)
        else:
            result = get_ticker_24h(symbol)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def compare_spot_futures_fees(
        symbol: str,
        price: float,
        quantity: float,
        leverage: int = 1,
    ) -> str:
        """Compare spot vs futures trading fees for a given order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            price: Order price in quote currency
            quantity: Order quantity in base currency
            leverage: Leverage for futures (default: 1)
        """
        result = compare_spot_vs_futures(price, quantity, leverage)
        result["symbol"] = symbol
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_kline_chart(
        symbol: str,
        interval: str = "1h",
        limit: int = 100,
        is_futures: bool = False,
    ) -> str:
        """Get candlestick/kline chart data for a trading pair. Use this when user asks to draw/show/display a chart or graph of price.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')
            interval: Kline interval - '1m','3m','5m','15m','30m','1h','2h','4h','6h','8h','12h','1d','3d','1w','1M' (default: '1h')
            limit: Number of candles to return, max 500 (default: 100)
            is_futures: Whether to use futures data (default: False)
        """
        result = get_klines(symbol, interval, limit, is_futures)
        if "error" in result:
            return json.dumps(result, indent=2)

        chart_id = uuid.uuid4().hex[:8]
        chart_result = {
            "chart_id": chart_id,
            "type": "candlestick",
            "symbol": result["symbol"],
            "interval": result["interval"],
            "is_futures": result["is_futures"],
            "count": result["count"],
            "candles": result["candles"],
        }
        return json.dumps(chart_result, ensure_ascii=False)
