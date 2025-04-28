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
import time
from typing import Dict, List, Optional, Any, Union

from config import get_logger
from services.binance.restAPI.base_operations import BinanceAPIRequest
from services.binance.models import SystemStatus, RateLimitType,ExchangeInfo
from config.mapper import mapper

logger = get_logger(__name__)

class SystemOperations:
    """
    Binance system API client using a single /exchangeInfo call and AutoMapper.
    Provides server time, system status, and unified exchange info access.
    """

    def __init__(self):
        pass

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
        response = (
            self.request("GET", "/api/v3/time", RateLimitType.REQUEST_WEIGHT, 1)
                .requires_auth(False)
                .execute()
        )
        if isinstance(response, dict) and 'serverTime' in response:
            return int(response['serverTime'])
        return int(time.time() * 1000)

    def getSystemStatus(self) -> SystemStatus:
        """
        GET /sapi/v1/system/status
        Returns SystemStatus dataclass (0: normal, 1: maintenance)
        """
        response = (
            self.request("GET", "/sapi/v1/system/status", RateLimitType.REQUEST_WEIGHT, 1)
                .requires_auth(False)
                .execute()
        ) or {}
        status_code = response.get('status', -1)
        return SystemStatus(status_code=status_code)

    def _exchangeInfo(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        show_permission_sets: bool = False,
        symbol_status: Optional[str] = None,
    ) -> ExchangeInfo:
        """
        Internal helper: single GET /api/v3/exchangeInfo call with weight=20,
        returning mapped ExchangeInfo dataclass.
        """
        params: Dict[str, Any] = {}
        if symbol:
            params['symbol'] = symbol
        if symbols:
            params['symbols'] = json.dumps(symbols)
        if permissions:
            params['permissions'] = json.dumps(permissions)
        if show_permission_sets:
            params['showPermissionSets'] = 'true'
        if symbol_status:
            params['symbolStatus'] = symbol_status

        raw = (
            self.request(
                "GET",
                "/api/v3/exchangeInfo",
                RateLimitType.REQUEST_WEIGHT,
                20,
            )
            .requires_auth(False)
            .with_query_params(**params)
            .execute()
        ) or {}

        return mapper.map(raw, ExchangeInfo)

    def getExchangeInfo(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        show_permission_sets: bool = False,
        symbol_status: Optional[str] = None,
    ) -> ExchangeInfo:
        """
        Public entry: Returns mapped ExchangeInfo for given filters.
        """
        return self._exchangeInfo(
            symbol=symbol,
            symbols=symbols,
            permissions=permissions,
            show_permission_sets=show_permission_sets,
            symbol_status=symbol_status,
        )
