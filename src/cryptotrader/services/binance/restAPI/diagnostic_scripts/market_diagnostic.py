"""
Binance Market API Diagnostic Script
------------------------------------
Tests the Binance Market API client to verify connectivity and data retrieval.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/market_diagnostic.py
"""

import sys
import traceback
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.restAPI import MarketOperations

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing


def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")


def main():
    logger.info(f"Added {project_root} to Python path")

    logger.info("Initializing Binance Market client...")
    client = MarketOperations()  # No need to pass API credentials

    # Test 1: Get bid/ask for BTC/USDT
    print_test_header("Getting current BTC/USDT price")
    try:
        btc_price = client.getBidAsk(TEST_SYMBOL)
        if btc_price:
            logger.info(f"BTC/USDT Bid: ${btc_price.bid:.2f}")
            logger.info(f"BTC/USDT Ask: ${btc_price.ask:.2f}")
        else:
            logger.error("Failed to retrieve BTC/USDT price")
    except Exception as e:
        logger.error(f"Error retrieving BTC/USDT price: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 2: Get historical candles
    print_test_header("Getting historical candles for BTC/USDT (1-hour interval)")
    try:
        candles = client.getHistoricalCandles(TEST_SYMBOL, "1h", limit=10)
        logger.info(f"Retrieved {len(candles)} candles")
        if candles:
            logger.info("Most recent candle:")
            logger.info(f"  Time: {candles[-1].timestamp}")
            logger.info(f"  Open: ${candles[-1].openPrice:.2f}")
            logger.info(f"  High: ${candles[-1].highPrice:.2f}")
            logger.info(f"  Low: ${candles[-1].lowPrice:.2f}")
            logger.info(f"  Close: ${candles[-1].closePrice:.2f}")
            logger.info(f"  Volume: {candles[-1].volume:.8f}")
        else:
            logger.error("Failed to retrieve candles for BTC/USDT")
    except Exception as e:
        logger.error(f"Error retrieving historical candles: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 3: Get ticker price for BTC/USDT
    print_test_header("Getting ticker price for BTC/USDT")
    try:
        ticker = client.getTickerPrice(TEST_SYMBOL)
        if ticker:
            logger.info(f"BTC/USDT Price: ${float(ticker.price):.2f}")
        else:
            logger.error("Failed to retrieve BTC/USDT ticker price")
    except Exception as e:
        logger.error(f"Error retrieving ticker price: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 4: Get average price for BTC/USDT
    print_test_header("Getting average price for BTC/USDT")
    try:
        avg_price = client.getAvgPriceRest(TEST_SYMBOL)
        if avg_price:
            logger.info(
                f"BTC/USDT Average Price (mins={avg_price.mins}): ${avg_price.price:.2f}"
            )
        else:
            logger.error("Failed to retrieve BTC/USDT average price")
    except Exception as e:
        logger.error(f"Error retrieving average price: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 5: Get order book
    print_test_header("Getting order book for BTC/USDT")
    try:
        order_book = client.getOrderBookRest(TEST_SYMBOL, limit=5)
        if order_book:
            logger.info(f"Order Book Last Update ID: {order_book.lastUpdateId}")
            logger.info(f"Top 5 Bids:")
            for i, bid in enumerate(order_book.bids[:5]):
                logger.info(
                    f"  {i + 1}. Price: ${bid.price:.2f}, Quantity: {bid.quantity:.8f}"
                )
            logger.info(f"Top 5 Asks:")
            for i, ask in enumerate(order_book.asks[:5]):
                logger.info(
                    f"  {i + 1}. Price: ${ask.price:.2f}, Quantity: {ask.quantity:.8f}"
                )
        else:
            logger.error("Failed to retrieve BTC/USDT order book")
    except Exception as e:
        logger.error(f"Error retrieving order book: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 6: Get 24-hour price statistics
    print_test_header("Getting 24-hour price statistics for BTC/USDT")
    try:
        stats = client.get24hStats(TEST_SYMBOL)
        if stats:
            logger.info(
                f"24h Price Change: ${stats.priceChange:.2f} ({stats.priceChangePercent:.2f}%)"
            )
            logger.info(f"24h High: ${stats.highPrice:.2f}")
            logger.info(f"24h Low: ${stats.lowPrice:.2f}")
            logger.info(f"24h Volume: {stats.volume:.8f} BTC")
            logger.info(f"24h Quote Volume: ${stats.quoteVolume:.2f}")
        else:
            logger.error("Failed to retrieve BTC/USDT 24-hour statistics")
    except Exception as e:
        logger.error(f"Error retrieving 24-hour statistics: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 7: Get Rolling Window Statistics
    print_test_header("Getting rolling window statistics for BTC/USDT")
    try:
        rolling_stats = client.getRollingWindowStatsRest(TEST_SYMBOL, window_size="1d")
        if rolling_stats:
            logger.info(
                f"1d Rolling Window Price Change: ${rolling_stats.priceChange:.2f} ({rolling_stats.priceChangePercent:.2f}%)"
            )
            logger.info(f"1d Window High: ${rolling_stats.highPrice:.2f}")
            logger.info(f"1d Window Low: ${rolling_stats.lowPrice:.2f}")
            logger.info(f"1d Window Volume: {rolling_stats.volume:.8f} BTC")
        else:
            logger.error("Failed to retrieve BTC/USDT rolling window statistics")
    except Exception as e:
        logger.error(f"Error retrieving rolling window statistics: {str(e)}")
        logger.debug(traceback.format_exc())

    # Summary
    logger.info("\nMarket API Diagnostic Summary:")
    logger.info("----------------------------")
    logger.info("The following tests were performed:")
    logger.info("1. Getting current BTC/USDT price")
    logger.info("2. Getting historical candles for BTC/USDT")
    logger.info("3. Getting ticker price for BTC/USDT")
    logger.info("4. Getting average price for BTC/USDT")
    logger.info("5. Getting order book for BTC/USDT")
    logger.info("6. Getting 24-hour price statistics for BTC/USDT")
    logger.info("7. Getting rolling window statistics for BTC/USDT")
    logger.info(
        "\nMarket API diagnostic completed. Check the logs above for any errors."
    )


if __name__ == "__main__":
    main()
