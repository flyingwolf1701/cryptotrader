"""
Binance REST API Unified Client

This module provides a unified client for interacting with the Binance REST API.
It combines the functionality from:
- Market data operations
- Order operations
- Wallet operations
- User account operations

The client automatically handles authentication and rate limiting through
the underlying implementation in base_operations.
"""

from typing import Dict, List, Optional, Any, Union

from .config import get_logger
from .services.binance.restAPI.market_api import MarketOperations
from .services.binance.restAPI.order_api import OrderOperations
from .services.binance.restAPI.wallet_api import WalletOperations
from .services.binance.restAPI.user_api import UserOperations
from services.binance.models import (
    # Market models
    PriceData,
    Candle,
    Trade,
    AggTrade,
    OrderBook,
    TickerPrice,
    AvgPrice,
    PriceStats,
    PriceStatsMini,
    RollingWindowStats,
    RollingWindowStatsMini,
    # Order models
    OrderRequest,
    OrderStatusResponse,
    OrderResponseFull,
    OrderResponseResult,
    OrderResponseAck,
    CancelReplaceResponse,
    OrderTrade,
    PreventedMatch,
    RateLimitInfo,
    OcoOrderResponse,
    # Wallet models
    AssetDetail,
    FiatWithdrawResponse,
    CryptoWithdrawResponse,
    WithdrawHistoryItem,
    FiatWithdrawHistory,
    DepositAddress,
    DepositHistoryItem,
    FiatDepositHistory,
    # User models
    AccountBalance,
)

logger = get_logger(__name__)


class BinanceRestUnifiedClient:
    """
    Unified client for Binance REST API.

    This client integrates the functionality from market data, order,
    wallet, and user account operations into a single, easy-to-use interface.
    Authentication and rate limiting are automatically handled by the underlying
    implementation in base_operations.
    """

    def __init__(self):
        """Initialize the unified client with all required operations."""
        self.market = MarketOperations()
        self.order = OrderOperations()
        self.wallet = WalletOperations()
        self.user = UserOperations()

        logger.info("Binance REST Unified Client initialized")

    # Market Data Methods

    def get_ticker_price(
        self, symbol: Optional[str] = None
    ) -> Union[TickerPrice, List[TickerPrice], None]:
        """
        Get live ticker price for a symbol or for all symbols.

        Args:
            symbol: Symbol to get price for (e.g. "BTCUSDT").
                  If None, prices for all symbols will be returned.

        Returns:
            TickerPrice object if symbol is provided, or list of TickerPrice objects for all symbols
        """
        return self.market.get_ticker_price(symbol)

    def get_historical_candles(
        self,
        symbol: str,
        interval: str,
        limit: int = 500,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[Candle]:
        """
        Get historical candlestick data.

        Args:
            symbol: Symbol to get candles for (e.g. "BTCUSDT")
            interval: Candle interval (e.g. "1m", "1h", "1d")
            limit: Number of candles to return (max 1000)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds

        Returns:
            List of Candle objects
        """
        return self.market.get_historical_candles(
            symbol, interval, limit, start_time, end_time
        )

    def get_order_book(self, symbol: str, limit: int = 100) -> Optional[OrderBook]:
        """
        Get order book (market depth) for a symbol.

        Args:
            symbol: Symbol to get order book for (e.g. "BTCUSDT")
            limit: Number of price levels to return. Default 100; max 5000.

        Returns:
            OrderBook object with bids and asks, or None if request fails
        """
        return self.market.get_order_book_rest(symbol, limit)

    def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Trade]:
        """
        Get recent trades for a symbol.

        Args:
            symbol: Symbol to get trades for (e.g. "BTCUSDT")
            limit: Number of trades to return (default 500, max 1000)

        Returns:
            List of Trade objects
        """
        return self.market.get_recent_trades_rest(symbol, limit)

    def get_24h_stats(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        type: Optional[str] = None,
    ) -> Union[
        Union[PriceStats, PriceStatsMini], List[Union[PriceStats, PriceStatsMini]], None
    ]:
        """
        Get 24-hour price change statistics for a symbol, multiple symbols, or all symbols.

        Args:
            symbol: Symbol to get statistics for (e.g. "BTCUSDT")
            symbols: List of symbols to get statistics for. Cannot be used with 'symbol'.
            type: Response type ("FULL" or "MINI").

        Returns:
            PriceStats/PriceStatsMini object or list of objects
        """
        return self.market.get_24h_stats(symbol, symbols, type)

    def get_avg_price(self, symbol: str) -> Optional[AvgPrice]:
        """
        Get current average price for a symbol.

        Args:
            symbol: Symbol to get average price for (e.g. "BTCUSDT")

        Returns:
            AvgPrice object with average price information
        """
        return self.market.get_avg_price(symbol)

    # Order Methods

    def place_order(
        self, order_request: Union[OrderRequest, Dict[str, Any]]
    ) -> Optional[OrderStatusResponse]:
        """
        Place a new order.

        Args:
            order_request: The order details as OrderRequest object or dictionary

        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        return self.order.place_spot_order(order_request)

    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        client_order_id: Optional[str] = None,
        newClientOrderId: Optional[str] = None,
        cancel_restrictions: Optional[str] = None,
    ) -> Optional[OrderStatusResponse]:
        """
        Cancel an existing order.

        Args:
            symbol: The symbol for the order (e.g. "BTCUSDT")
            order_id: The order ID assigned by Binance
            client_order_id: The client order ID if used when placing the order
            newClientOrderId: Used to uniquely identify this cancel
            cancel_restrictions: Conditions for cancellation (ONLY_NEW, ONLY_PARTIALLY_FILLED)

        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        return self.order.cancel_order(
            symbol, order_id, client_order_id, newClientOrderId, cancel_restrictions
        )

    def get_order_status(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        client_order_id: Optional[str] = None,
    ) -> Optional[OrderStatusResponse]:
        """
        Get status of an existing order.

        Args:
            symbol: The symbol for the order (e.g. "BTCUSDT")
            order_id: The order ID assigned by Binance
            client_order_id: The client order ID if used when placing the order

        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        return self.order.get_order_status(symbol, order_id, client_order_id)

    def get_open_orders(
        self, symbol: Optional[str] = None
    ) -> List[OrderStatusResponse]:
        """
        Get all open orders on a symbol or all symbols.

        Args:
            symbol: Optional symbol to get open orders for (e.g. "BTCUSDT")
                  If None, gets orders for all symbols

        Returns:
            List of OrderStatusResponse objects with open order details
        """
        return self.order.get_open_orders(symbol)

    def get_my_trades(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        from_id: Optional[int] = None,
        limit: int = 500,
    ) -> List[OrderTrade]:
        """
        Get trades for a specific symbol.

        Args:
            symbol: The symbol to get trades for (e.g. "BTCUSDT")
            order_id: If specified, get trades for this order ID
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            from_id: TradeId to fetch from (gets trades >= from_id)
            limit: Maximum number of trades to return (default 500, max 1000)

        Returns:
            List of OrderTrade objects with trade details
        """
        return self.order.get_my_trades(
            symbol, order_id, start_time, end_time, from_id, limit
        )

    # Wallet Methods

    def get_asset_details(self, recv_window: Optional[int] = None) -> List[AssetDetail]:
        """
        Get details of all assets including fees, withdrawal limits, and network status.

        Args:
            recv_window: The value cannot be greater than 60000

        Returns:
            List of AssetDetail objects
        """
        return self.wallet.get_asset_details(recv_window)

    def get_deposit_address(
        self,
        coin: str,
        network: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Optional[DepositAddress]:
        """
        Get deposit address for a particular crypto asset.

        Args:
            coin: The coin to get address for
            network: The network to use
            recv_window: The value cannot be greater than 60000

        Returns:
            DepositAddress object with the address details, or None if the request failed
        """
        return self.wallet.get_deposit_address(coin, network, recv_window)

    def withdraw_crypto(
        self,
        coin: str,
        network: str,
        address: str,
        amount: Union[str, float],
        withdraw_order_id: Optional[str] = None,
        address_tag: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Optional[CryptoWithdrawResponse]:
        """
        Submit a crypto withdrawal request.

        Args:
            coin: The coin to withdraw
            network: Specify the withdrawal network (e.g. 'ERC20' or 'BEP20')
            address: The recipient address
            amount: The amount to withdraw
            withdraw_order_id: Client ID for the withdrawal
            address_tag: Memo for coins like XRP, XMR etc.
            recv_window: The value cannot be greater than 60000

        Returns:
            CryptoWithdrawResponse object with the withdrawal ID, or None if the request failed
        """
        return self.wallet.withdraw_crypto(
            coin, network, address, amount, withdraw_order_id, address_tag, recv_window
        )

    def get_crypto_deposit_history(
        self,
        coin: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        recv_window: Optional[int] = None,
    ) -> List[DepositHistoryItem]:
        """
        Get crypto deposit history.

        Args:
            coin: Filter by coin
            status: Filter by status (0: pending, 6: credited but cannot withdraw, 1: success)
            start_time: Start timestamp (default: 90 days from current timestamp)
            end_time: End timestamp (default: present timestamp)
            offset: Default: 0
            limit: Default: 1000, max: 1000
            recv_window: The value cannot be greater than 60000

        Returns:
            List of DepositHistoryItem objects
        """
        return self.wallet.get_crypto_deposit_history(
            coin, status, start_time, end_time, offset, limit, recv_window
        )

    def get_crypto_withdraw_history(
        self,
        coin: Optional[str] = None,
        withdraw_order_id: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        recv_window: Optional[int] = None,
    ) -> List[WithdrawHistoryItem]:
        """
        Get crypto withdrawal history.

        Args:
            coin: Filter by coin
            withdraw_order_id: Client ID for the withdrawal
            status: Filter by status (0: email sent, 1: canceled, 2: awaiting approval,
                   3: rejected, 4: processing, 5: failure, 6: completed)
            start_time: Start timestamp (default: 90 days from current timestamp)
            end_time: End timestamp (default: present timestamp)
            offset: Default: 0
            limit: Default: 1000, max: 1000
            recv_window: The value cannot be greater than 60000

        Returns:
            List of WithdrawHistoryItem objects
        """
        return self.wallet.get_crypto_withdraw_history(
            coin,
            withdraw_order_id,
            status,
            start_time,
            end_time,
            offset,
            limit,
            recv_window,
        )

    # User Account Methods

    def get_account(
        self, recv_window: Optional[int] = None
    ) -> Optional[AccountBalance]:
        """
        Get account information including balances.

        Args:
            recv_window: The value cannot be greater than 60000

        Returns:
            AccountBalance object with asset balances
        """
        return self.user.get_account(recv_window)

    def get_account_status(
        self, recv_window: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get account status.

        Args:
            recv_window: The value cannot be greater than 60000

        Returns:
            Dictionary with account status information
        """
        return self.user.get_account_status(recv_window)

    def get_trading_volume(self) -> Optional[Dict[str, Any]]:
        """
        Get past 30 days trading volume.

        Returns:
            Dictionary with trading volume information
        """
        return self.user.get_trading_volume()

    def get_trade_fee(
        self, symbol: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get trading fee information.

        Args:
            symbol: Symbol name, if not specified, will return all

        Returns:
            List of dictionaries with trading fee information
        """
        return self.user.get_trade_fee(symbol)
