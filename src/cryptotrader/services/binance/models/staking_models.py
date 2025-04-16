"""
Binance Staking API Models

This module defines the data structures for the Binance Staking API.
It provides strongly-typed models for staking-related operations including
asset information, staking/unstaking, balances, history, and rewards.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union


class StakingTransactionType(str, Enum):
    """Staking transaction types returned by Binance API"""
    STAKED = "staked"
    UNSTAKED = "unstaked"
    REWARD = "reward"


class StakingTransactionStatus(str, Enum):
    """Staking transaction status returned by Binance API"""
    SUCCESS = "SUCCESS"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"


@dataclass
class StakingAssetInfo:
    """Data structure for staking asset information"""
    stakingAsset: str
    rewardAsset: str
    apr: str
    apy: str
    unstakingPeriod: int
    minStakingLimit: str
    maxStakingLimit: str
    autoRestake: bool

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'StakingAssetInfo':
        return cls(
            stakingAsset=response['stakingAsset'],
            rewardAsset=response['rewardAsset'],
            apr=response['apr'],
            apy=response['apy'],
            unstakingPeriod=int(response['unstakingPeriod']),
            minStakingLimit=response['minStakingLimit'],
            maxStakingLimit=response['maxStakingLimit'],
            autoRestake=response['autoRestake']
        )


@dataclass
class StakingOperationResult:
    """Data structure for staking operation result"""
    code: str
    message: str
    data: Dict[str, Any]
    success: bool

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'StakingOperationResult':
        return cls(
            code=response['code'],
            message=response['message'],
            data=response['data'],
            success=response['success']
        )


@dataclass
class StakingStakeResult:
    """Data structure for stake operation result"""
    result: str
    purchaseRecordId: str

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'StakingStakeResult':
        data = response.get('data', {})
        return cls(
            result=data.get('result', ''),
            purchaseRecordId=data.get('purchaseRecordId', '')
        )


@dataclass
class StakingUnstakeResult:
    """Data structure for unstake operation result"""
    result: str

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'StakingUnstakeResult':
        data = response.get('data', {})
        return cls(
            result=data.get('result', '')
        )


@dataclass
class StakingBalanceItem:
    """Data structure for a single staking balance item"""
    asset: str
    stakingAmount: str
    rewardAsset: str
    apr: str
    apy: str
    autoRestake: bool

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'StakingBalanceItem':
        return cls(
            asset=response['asset'],
            stakingAmount=response['stakingAmount'],
            rewardAsset=response['rewardAsset'],
            apr=response['apr'],
            apy=response['apy'],
            autoRestake=response['autoRestake']
        )


@dataclass
class StakingBalanceResponse:
    """Data structure for staking balance response"""
    code: str
    message: str
    data: List[StakingBalanceItem]
    status: List[str]
    success: bool

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'StakingBalanceResponse':
        data_items = []
        for item in response.get('data', []):
            data_items.append(StakingBalanceItem.from_api_response(item))
        
        return cls(
            code=response['code'],
            message=response['message'],
            data=data_items,
            status=response.get('status', []),
            success=response['success']
        )


@dataclass
class StakingHistoryItem:
    """Data structure for staking history item"""
    asset: str
    amount: str
    type: StakingTransactionType
    initiatedTime: int
    status: StakingTransactionStatus

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'StakingHistoryItem':
        return cls(
            asset=response['asset'],
            amount=response['amount'],
            type=StakingTransactionType(response['type']),
            initiatedTime=int(response['initiatedTime']),
            status=StakingTransactionStatus(response['status'])
        )


@dataclass
class StakingRewardItem:
    """Data structure for staking reward item"""
    asset: str
    amount: str
    usdValue: str
    time: int
    tranId: int
    autoRestaked: bool

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'StakingRewardItem':
        return cls(
            asset=response['asset'],
            amount=response['amount'],
            usdValue=response['usdValue'],
            time=int(response['time']),
            tranId=int(response['tranId']),
            autoRestaked=response['autoRestaked']
        )


@dataclass
class StakingRewardsResponse:
    """Data structure for staking rewards response"""
    code: str
    message: str
    data: List[StakingRewardItem]
    total: int
    success: bool

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'StakingRewardsResponse':
        reward_items = []
        for item in response.get('data', []):
            reward_items.append(StakingRewardItem.from_api_response(item))
        
        return cls(
            code=response['code'],
            message=response['message'],
            data=reward_items,
            total=int(response.get('total', 0)),
            success=response['success']
        )
    