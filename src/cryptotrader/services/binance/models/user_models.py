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
    def from_api_response(cls, asset_data: Dict[str, Any]) -> 'AccountAsset':
        return cls(
            asset=asset_data['asset'],
            free=float(asset_data.get('free', 0)),
            locked=float(asset_data.get('locked', 0))
        )


@dataclass
class AccountBalance:
    """Data structure for account balance"""
    assets: Dict[str, AccountAsset]
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'AccountBalance':
        assets = {}
        for asset_data in response.get('balances', []):
            asset_name = asset_data['asset']
            assets[asset_name] = AccountAsset.from_api_response(asset_data)
        return cls(assets=assets)