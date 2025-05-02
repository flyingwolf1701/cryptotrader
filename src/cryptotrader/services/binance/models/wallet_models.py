"""
Binance Wallet API Models

This module defines the data structures for the Binance Wallet API.
It provides strongly-typed models for wallet-related operations including
asset details, deposit/withdrawal history, and network information.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union


class WithdrawStatus(int, Enum):
    """Withdraw status codes returned by Binance API"""
    EMAIL_SENT = 0       # Email sent
    CANCELED = 1         # Canceled
    AWAITING_APPROVAL = 2 # Awaiting approval
    REJECTED = 3         # Rejected
    PROCESSING = 4       # Processing
    FAILURE = 5          # Failure
    COMPLETED = 6        # Completed


class DepositStatus(int, Enum):
    """Deposit status codes returned by Binance API"""
    PENDING = 0          # Pending
    SUCCESS = 1          # Success
    CREDITED_NO_WITHDRAW = 6  # Credited but cannot withdraw


@dataclass
class NetworkInfo:
    """Data structure for network information of a coin"""
    network: str
    coin: str
    withdrawIntegerMultiple: str
    isDefault: bool
    depositEnable: bool
    withdrawEnable: bool
    depositDesc: str
    withdrawDesc: str
    name: str
    resetAddressStatus: bool
    withdrawFee: str
    withdrawMin: str
    withdrawMax: str
    minConfirm: Optional[int] = None
    unLockConfirm: Optional[int] = None
    addressRegex: Optional[str] = None
    memoRegex: Optional[str] = None
    specialTips: Optional[str] = None

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'NetworkInfo':
        return cls(
            network=response['network'],
            coin=response['coin'],
            withdrawIntegerMultiple=response['withdrawIntegerMultiple'],
            isDefault=response['isDefault'],
            depositEnable=response['depositEnable'],
            withdrawEnable=response['withdrawEnable'],
            depositDesc=response['depositDesc'],
            withdrawDesc=response['withdrawDesc'],
            name=response['name'],
            resetAddressStatus=response['resetAddressStatus'],
            withdrawFee=response['withdrawFee'],
            withdrawMin=response['withdrawMin'],
            withdrawMax=response['withdrawMax'],
            minConfirm=response.get('minConfirm'),
            unLockConfirm=response.get('unLockConfirm'),
            addressRegex=response.get('addressRegex'),
            memoRegex=response.get('memoRegex'),
            specialTips=response.get('specialTips')
        )


@dataclass
class AssetDetail:
    """Data structure for asset details"""
    coin: str
    depositAllEnable: bool
    withdrawAllEnable: bool
    name: str
    free: str
    locked: str
    freeze: str
    withdrawing: str
    ipoing: str
    ipoable: str
    storage: str
    isLegalMoney: bool
    trading: bool
    networkList: List[NetworkInfo]

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'AssetDetail':
        network_list = []
        if 'networkList' in response:
            for network_data in response['networkList']:
                network_list.append(NetworkInfo.from_api_response(network_data))

        return cls(
            coin=response['coin'],
            depositAllEnable=response['depositAllEnable'],
            withdrawAllEnable=response['withdrawAllEnable'],
            name=response['name'],
            free=response['free'],
            locked=response['locked'],
            freeze=response['freeze'],
            withdrawing=response['withdrawing'],
            ipoing=response['ipoing'],
            ipoable=response['ipoable'],
            storage=response['storage'],
            isLegalMoney=response['isLegalMoney'],
            trading=response['trading'],
            networkList=network_list
        )


@dataclass
class FiatWithdrawResponse:
    """Data structure for fiat withdrawal response"""
    orderId: str
    channelCode: str
    currencyCode: str
    amount: str
    orderStatus: str

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'FiatWithdrawResponse':
        return cls(
            orderId=response['orderId'],
            channelCode=response['channelCode'],
            currencyCode=response['currencyCode'],
            amount=response['amount'],
            orderStatus=response['orderStatus']
        )


@dataclass
class CryptoWithdrawResponse:
    """Data structure for crypto withdrawal response"""
    id: str

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'CryptoWithdrawResponse':
        return cls(
            id=response['id']
        )


@dataclass
class WithdrawHistoryItem:
    """Data structure for withdrawal history item"""
    id: str
    amount: str
    transactionFee: str
    coin: str
    status: WithdrawStatus
    address: str
    applyTime: str
    network: str
    transferType: int

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'WithdrawHistoryItem':
        return cls(
            id=response['id'],
            amount=response['amount'],
            transactionFee=response['transactionFee'],
            coin=response['coin'],
            status=WithdrawStatus(response['status']),
            address=response['address'],
            applyTime=response['applyTime'],
            network=response['network'],
            transferType=int(response['transferType'])
        )


@dataclass
class FiatWithdrawHistoryItem:
    """Data structure for fiat withdrawal history item"""
    orderId: str
    paymentAccount: str
    paymentChannel: str
    paymentMethod: str
    orderStatus: str
    amount: str
    transactionFee: str
    platformFee: str

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'FiatWithdrawHistoryItem':
        return cls(
            orderId=response['orderId'],
            paymentAccount=response['paymentAccount'],
            paymentChannel=response['paymentChannel'],
            paymentMethod=response['paymentMethod'],
            orderStatus=response['orderStatus'],
            amount=response['amount'],
            transactionFee=response['transactionFee'],
            platformFee=response['platformFee']
        )


@dataclass
class FiatWithdrawHistory:
    """Data structure for fiat withdrawal history"""
    assetLogRecordList: List[FiatWithdrawHistoryItem]

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'FiatWithdrawHistory':
        asset_log_records = []
        for record in response.get('assetLogRecordList', []):
            asset_log_records.append(FiatWithdrawHistoryItem.from_api_response(record))
        
        return cls(
            assetLogRecordList=asset_log_records
        )


@dataclass
class DepositAddress:
    """Data structure for deposit address"""
    coin: str
    address: str
    tag: str
    url: str

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'DepositAddress':
        return cls(
            coin=response['coin'],
            address=response['address'],
            tag=response['tag'],
            url=response.get('url', '')
        )


@dataclass
class DepositHistoryItem:
    """Data structure for deposit history item"""
    amount: str
    coin: str
    network: str
    status: DepositStatus
    address: str
    addressTag: str
    txId: str
    insertTime: int
    transferType: int
    confirmTimes: str

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'DepositHistoryItem':
        return cls(
            amount=response['amount'],
            coin=response['coin'],
            network=response['network'],
            status=DepositStatus(response['status']),
            address=response['address'],
            addressTag=response['addressTag'],
            txId=response['txId'],
            insertTime=int(response['insertTime']),
            transferType=int(response['transferType']),
            confirmTimes=response['confirmTimes']
        )


@dataclass
class FiatDepositHistoryItem:
    """Data structure for fiat deposit history item"""
    orderId: str
    paymentAccount: str
    paymentChannel: str
    paymentMethod: str
    orderStatus: str
    fiatCurrency: str
    amount: str
    transactionFee: str
    platformFee: str

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'FiatDepositHistoryItem':
        return cls(
            orderId=response['orderId'],
            paymentAccount=response['paymentAccount'],
            paymentChannel=response['paymentChannel'],
            paymentMethod=response['paymentMethod'],
            orderStatus=response['orderStatus'],
            fiatCurrency=response['fiatCurrency'],
            amount=response['amount'],
            transactionFee=response['transactionFee'],
            platformFee=response['platformFee']
        )


@dataclass
class FiatDepositHistory:
    """Data structure for fiat deposit history"""
    assetLogRecordList: List[FiatDepositHistoryItem]

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'FiatDepositHistory':
        asset_log_records = []
        for record in response.get('assetLogRecordList', []):
            asset_log_records.append(FiatDepositHistoryItem.from_api_response(record))
        
        return cls(
            assetLogRecordList=asset_log_records
        )
