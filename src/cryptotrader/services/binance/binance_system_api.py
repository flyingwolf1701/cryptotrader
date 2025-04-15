"""
Binance System API Client

This module provides a client for interacting with Binance system-wide API endpoints.
It includes functionality for:
- Server time retrieval
- System status checks
- Exchange information retrieval

These endpoints provide information about the Binance platform itself rather
than specific market data or trading operations.
"""

import json
import time  # Need to add this for the fallback time function
from typing import Dict, List, Optional, Any, Union

from cryptotrader.config import get_logger
from cryptotrader.services.binance.binance_base_operations import BinanceAPIRequest
from cryptotrader.services.binance.binance_models import (
    SystemStatus, SymbolInfo, RateLimitType
)

logger = get_logger(__name__)

class SystemClient:
    """
    Binance system API client implementation.
    
    Provides methods for checking system status, getting server time,
    and retrieving exchange information.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize the System client."""
        self.api_key = api_key
        self.api_secret = api_secret
    
    def request(self, method: str, endpoint: str, 
               limit_type: Optional[RateLimitType] = None,
               weight: int = 1) -> BinanceAPIRequest:
        """Create a new API request."""
        return BinanceAPIRequest(
            method=method, 
            endpoint=endpoint,
            limit_type=limit_type,
            weight=weight
        )
    
    def get_server_time(self) -> int:
        """
        Get current server time from Binance API.
        
        Weight: 1
        
        Returns:
            Server time in milliseconds
        """
        response = self.request("GET", "/api/v3/time").requires_auth(False).execute()
        if response:
            return response["serverTime"]
        return int(time.time() * 1000)  # Fallback to local time
    
    def get_system_status(self) -> SystemStatus:
        """
        Get system status.
        
        Weight: 1
        
        Returns:
            SystemStatus object (0: normal, 1: maintenance)
        """
        # FIX: Changed requires_api_key to requires_auth
        response = self.request("GET", "/sapi/v1/system/status").requires_auth(True).execute()
        if response:
            return SystemStatus(status_code=response.get("status", -1))
        return SystemStatus(status_code=-1)  # Unknown status
    
    def get_exchange_info(self, symbol: Optional[str] = None,
                        symbols: Optional[List[str]] = None,
                        permissions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get exchange information.
        
        Weight: 1 for a single symbol, 10 for all symbols
        
        Args:
            symbol: Single symbol to get info for
            symbols: Multiple symbols to get info for
            permissions: Permissions to filter by (e.g. ["SPOT"])
            
        Returns:
            Dictionary containing exchange information
        """
        request = self.request("GET", "/api/v3/exchangeInfo").requires_auth(False)
        
        if symbol:
            request.with_query_params(symbol=symbol)
        elif symbols:
            symbols_str = json.dumps(symbols)
            request.with_query_params(symbols=symbols_str)
        elif permissions:
            permissions_str = json.dumps(permissions)
            request.with_query_params(permissions=permissions_str)
        
        response = request.execute()
        return response if response else {}
    
    def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        """
        Get information for a specific symbol.
        
        Weight: 1
        
        Args:
            symbol: The symbol to get information for (e.g. "BTCUSDT")
            
        Returns:
            SymbolInfo object with symbol details, or None if not found
        """
        exchange_info = self.get_exchange_info(symbol=symbol)
        if 'symbols' in exchange_info and exchange_info['symbols']:
            symbol_data = exchange_info['symbols'][0]
            return SymbolInfo.from_api_response(symbol_data)
        return None
    
    def get_self_trade_prevention_modes(self) -> Dict[str, Any]:
        """
        Get self-trade prevention modes from exchange info.
        
        Weight: 1
        
        Returns:
            Dictionary with default and allowed modes
        """
        exchange_info = self.get_exchange_info()
        if 'selfTradePreventionModes' in exchange_info:
            stp_modes = {'allowed': exchange_info['selfTradePreventionModes']}
            if 'defaultSelfTradePreventionMode' in exchange_info:
                stp_modes['default'] = exchange_info['defaultSelfTradePreventionMode']
            return stp_modes
        return {'default': 'NONE', 'allowed': []}
    
    @staticmethod
    def get_symbols_binance() -> List[str]:
        """
        Get available trading symbols.
        
        Weight: 10
        
        Returns:
            List of available trading symbols
        """
        client = SystemClient()
        response = client.request("GET", "/api/v3/exchangeInfo").requires_auth(False).execute()
        
        symbols = []
        if response and 'symbols' in response:
            symbols = [s['symbol'] for s in response['symbols'] 
                    if s['status'] == 'TRADING']
        return symbols