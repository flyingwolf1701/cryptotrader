"""
Binance System API Client

This module provides a client for interacting with Binance system-wide API endpoints.
It includes functionality for:
- Server time retrieval
- System status checks
- Exchange information retrieval (with in-memory caching)
- Helpers for symbol lookup

These endpoints provide information about the Binance platform itself rather
than specific market data or trading operations.
"""

import json
import time
from typing import Dict, List, Optional, Any, Set

from config import get_logger
from services.binance.models.base_models import (
    ExchangeInfo,
    SymbolInfo,
    SymbolStatus,
)
from services.binance.models import SystemStatus, RateLimitType
from services.binance.restAPI.baseOperations import BinanceAPIRequest

logger = get_logger(__name__)


class SystemOperations:
    """
    Binance system API client.  
    Provides:
      - getServerTime()
      - getSystemStatus()
      - getExchangeInfo() with full dataclass parsing
      - get_symbols(): map symbol→SymbolInfo
      - get_binance_symbols(): cached Set[str] of symbols
    """

    def __init__(self):
        # In-memory cache for the last-fetched ExchangeInfo
        self._exchange_info_cache: Optional[ExchangeInfo] = None

    def request(
        self,
        method: str,
        endpoint: str,
        limit_type: Optional[RateLimitType] = None,
        weight: int = 1,
    ) -> BinanceAPIRequest:
        return BinanceAPIRequest(
            method=method,
            endpoint=endpoint,
            limit_type=limit_type,
            weight=weight,
        )

    def getServerTime(self) -> int:
        """
        GET /api/v3/time
        Returns server time in milliseconds.
        """
        resp = (
            self.request("GET", "/api/v3/time", RateLimitType.REQUEST_WEIGHT, 1)
            .requiresAuth(False)
            .execute()
        )
        if isinstance(resp, dict) and "serverTime" in resp:
            return int(resp["serverTime"])
        return int(time.time() * 1000)

    def getSystemStatus(self) -> SystemStatus:
        """
        GET /sapi/v1/system/status
        Returns SystemStatus dataclass with:
          status_code: 0 = normal, 1 = maintenance
        """
        resp = (
            self.request("GET", "/sapi/v1/system/status", RateLimitType.REQUEST_WEIGHT, 1)
            .requiresAuth(False)
            .execute()
        ) or {}
        return SystemStatus(status_code=resp.get("status", -1))

    def _exchangeInfo(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        show_permission_sets: bool = False,
        symbol_status: Optional[str] = None,
    ) -> ExchangeInfo:
        """
        Internal helper: GET /api/v3/exchangeInfo (weight=20)
        Returns parsed ExchangeInfo dataclass.
        """
        params: Dict[str, Any] = {}
        if symbol:
            params["symbol"] = symbol
        if symbols:
            params["symbols"] = json.dumps(symbols)
        if permissions:
            params["permissions"] = json.dumps(permissions)
        if show_permission_sets:
            params["showPermissionSets"] = "true"
        if symbol_status:
            params["symbolStatus"] = symbol_status

        raw = (
            self.request("GET", "/api/v3/exchangeInfo", RateLimitType.REQUEST_WEIGHT, 20)
            .requiresAuth(False)
            .withQueryParams(**params)
            .execute()
        ) or {}

        return ExchangeInfo.from_api_response(raw)

    def getExchangeInfo(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        show_permission_sets: bool = False,
        symbol_status: Optional[str] = None,
    ) -> ExchangeInfo:
        """
        Public entry point for exchangeInfo.
        Applies the same filters as _exchangeInfo.
        """
        return self._exchangeInfo(
            symbol=symbol,
            symbols=symbols,
            permissions=permissions,
            show_permission_sets=show_permission_sets,
            symbol_status=symbol_status,
        )

    def refresh_exchange_info(self) -> None:
        """
        Clears the cached ExchangeInfo.
        Next call to get_binance_symbols or get_symbols will fetch fresh data.
        """
        self._exchange_info_cache = None

    def get_symbols(self) -> Dict[str, SymbolInfo]:
        """
        Returns a dict mapping symbol string → SymbolInfo object for all symbols.
        Uses cached ExchangeInfo if available.
        """
        if self._exchange_info_cache is None:
            self._exchange_info_cache = self.getExchangeInfo()
        return {s.symbol: s for s in self._exchange_info_cache.symbols}

    def get_binance_symbols(self, only_trading: bool = True) -> Set[str]:
        """
        Returns a set of symbol strings.
        
        Args:
          only_trading: if True, only include symbols whose status == TRADING.
        
        Uses in-memory cache; call refresh_exchange_info() to refetch.
        """
        if self._exchange_info_cache is None:
            self._exchange_info_cache = self.getExchangeInfo()

        symbols = self._exchange_info_cache.symbols
        if only_trading:
            return {s.symbol for s in symbols if s.status == SymbolStatus.TRADING}
        return {s.symbol for s in symbols}
