"""
Binance OTC API Models

This module defines the data structures for the Binance OTC (Over-The-Counter) API.
It provides strongly-typed models for OTC trading operations including coin pairs,
quotes, and order information.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any


class OtcOrderStatus(str, Enum):
    """OTC order statuses returned by Binance API"""
    PROCESS = "PROCESS"               # Order is being processed
    ACCEPT_SUCCESS = "ACCEPT_SUCCESS" # Order accepted successfully
    SUCCESS = "SUCCESS"               # Order completed successfully
    FAIL = "FAIL"                     # Order failed


@dataclass
class OtcCoinPair:
    """Data structure for OTC supported coin pairs"""
    fromCoin: str
    toCoin: str
    fromCoinMinAmount: float
    fromCoinMaxAmount: float
    toCoinMinAmount: float
    toCoinMaxAmount: float

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OtcCoinPair':
        return cls(
            fromCoin=response['fromCoin'],
            toCoin=response['toCoin'],
            fromCoinMinAmount=float(response['fromCoinMinAmount']),
            fromCoinMaxAmount=float(response['fromCoinMaxAmount']),
            toCoinMinAmount=float(response['toCoinMinAmount']),
            toCoinMaxAmount=float(response['toCoinMaxAmount'])
        )


@dataclass
class OtcQuote:
    """Data structure for OTC quote information"""
    symbol: str
    ratio: float
    inverseRatio: float
    validTimestamp: int
    toAmount: float
    fromAmount: float
    quoteId: Optional[str] = None  # Not in the original response, but useful for tracking

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OtcQuote':
        return cls(
            symbol=response['symbol'],
            ratio=float(response['ratio']),
            inverseRatio=float(response['inverseRatio']),
            validTimestamp=int(response['validTimestamp']),
            toAmount=float(response['toAmount']),
            fromAmount=float(response['fromAmount']),
            quoteId=response.get('quoteId')
        )


@dataclass
class OtcOrderResponse:
    """Data structure for OTC order creation response"""
    orderId: str
    createTime: int
    orderStatus: OtcOrderStatus

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OtcOrderResponse':
        return cls(
            orderId=response['orderId'],
            createTime=int(response['createTime']),
            orderStatus=OtcOrderStatus(response['orderStatus'])
        )


@dataclass
class OtcOrderDetail:
    """Data structure for OTC order details"""
    quoteId: str
    orderId: str
    orderStatus: OtcOrderStatus
    fromCoin: str
    fromAmount: float
    toCoin: str
    toAmount: float
    ratio: float
    inverseRatio: float
    createTime: int

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OtcOrderDetail':
        return cls(
            quoteId=response['quoteId'],
            orderId=response['orderId'],
            orderStatus=OtcOrderStatus(response['orderStatus']),
            fromCoin=response['fromCoin'],
            fromAmount=float(response['fromAmount']),
            toCoin=response['toCoin'],
            toAmount=float(response['toAmount']),
            ratio=float(response['ratio']),
            inverseRatio=float(response.get('inverseRatio', 0)),
            createTime=int(response['createTime'])
        )


@dataclass
class OtcOrdersResponse:
    """Data structure for OTC orders list response"""
    total: int
    rows: List[OtcOrderDetail]

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OtcOrdersResponse':
        return cls(
            total=int(response['total']),
            rows=[OtcOrderDetail.from_api_response(order) for order in response['rows']]
        )


@dataclass
class OcbsOrderDetail:
    """Data structure for OCBS order details"""
    quoteId: str
    orderId: str
    orderStatus: OtcOrderStatus
    fromCoin: str
    fromAmount: float
    toCoin: str
    toAmount: float
    feeCoin: str
    feeAmount: float
    ratio: float
    createTime: int

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OcbsOrderDetail':
        return cls(
            quoteId=response['quoteId'],
            orderId=response['orderId'],
            orderStatus=OtcOrderStatus(response['orderStatus']),
            fromCoin=response['fromCoin'],
            fromAmount=float(response['fromAmount']),
            toCoin=response['toCoin'],
            toAmount=float(response['toAmount']),
            feeCoin=response['feeCoin'],
            feeAmount=float(response['feeAmount']),
            ratio=float(response['ratio']),
            createTime=int(response['createTime'])
        )


@dataclass
class OcbsOrdersResponse:
    """Data structure for OCBS orders list response"""
    total: int
    dataList: List[OcbsOrderDetail]

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OcbsOrdersResponse':
        return cls(
            total=int(response['total']),
            dataList=[OcbsOrderDetail.from_api_response(order) for order in response['dataList']]
        )
