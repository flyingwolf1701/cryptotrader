# File: src/cryptotrader/services/crypto/restAPI/crypto_api.py
"""
Crypto.com API endpoints (Market, Account, Orders).
Provides free functions to interact with CryptoBaseOperations.
"""
from typing import Any, Dict, List, Optional
from cryptotrader.services.crypto.restAPI.crypto_api_request import CryptoBaseOperations


def get_exchange_info(client: CryptoBaseOperations) -> Dict[str, Any]:
    """Return symbol metadata (mirror Binance get_exchange_info)."""
    return client._request("GET", "/public/get-instruments")


def get_ticker_24h(client: CryptoBaseOperations, instrument_name: str) -> Dict[str, Any]:
    """24h stats; instrument_name like "BTC_USDT"."""
    return client._request(
        "GET", "/public/get-ticker", instrument_name=instrument_name
    )


def get_account_summary(client: CryptoBaseOperations) -> Dict[str, Any]:
    """Retrieve account balances and summary."""
    return client._request("POST", "/private/get-account-summary")


def place_order(
    client: CryptoBaseOperations,
    instrument_name: str,
    side: str,
    type_: str,
    quantity: float,
    price: Optional[float] = None,
) -> Dict[str, Any]:
    """Place a new order (LIMIT or MARKET)."""
    return client._request(
        "POST",
        "/private/create-order",
        instrument_name=instrument_name,
        side=side,
        type=type_,
        price=price,
        quantity=quantity,
    )


def cancel_order(client: CryptoBaseOperations, order_id: str) -> Dict[str, Any]:
    """Cancel an existing order by ID."""
    return client._request("POST", "/private/cancel-order", order_id=order_id)


def get_my_trades(
    client: CryptoBaseOperations, instrument_name: str, **kwargs
) -> List[Dict[str, Any]]:
    """Fetch recent trades for an instrument."""
    res = client._request(
        "POST", "/private/get-trades", instrument_name=instrument_name, **kwargs
    )
    return res.get("data", [])