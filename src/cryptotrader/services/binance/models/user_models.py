"""
Binance User API Models

This module defines the data structures used by the Binance User API client.
It provides strongly-typed models for user account information and operations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class AccountAsset:
    """Data structure for account asset"""

    asset: str
    free: float
    locked: float

    @classmethod
    def from_api_response(cls, assetData: Dict[str, Any]) -> "AccountAsset":
        return cls(
            asset=assetData["asset"],
            free=float(assetData.get("free", 0)),
            locked=float(assetData.get("locked", 0)),
        )


@dataclass
class AccountBalance:
    """Data structure for account balance"""

    assets: Dict[str, AccountAsset]

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "AccountBalance":
        assets = {}
        for assetData in response.get("balances", []):
            assetName = assetData["asset"]
            assets[assetName] = AccountAsset.from_api_response(assetData)
        return cls(assets=assets)
