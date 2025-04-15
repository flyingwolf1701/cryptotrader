"""
Binance Order API Models

This module defines the data structures and enumerations specific to the Binance Order API.
It provides strongly-typed models for order-related requests and responses.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union

# Import base models to reference common types
from cryptotrader.services.binance.models.base_models import OrderStatus, OrderType, OrderSide, TimeInForce


class CancelReplaceMode(str, Enum):
    """Cancel-replace modes supported by Binance API"""
    STOP_ON_FAILURE = "STOP_ON_FAILURE"  # If cancel fails, new order won't be placed
    ALLOW_FAILURE = "ALLOW_FAILURE"      # New order placement attempted even if cancel fails


class NewOrderResponseType(str, Enum):
    """Response type options for order placement"""
    ACK = "ACK"        # Only acknowledgment, minimal response
    RESULT = "RESULT"  # Response with execution result
    FULL = "FULL"      # Full response with fills


class CancelRestriction(str, Enum):
    """Restrictions for order cancellation"""
    ONLY_NEW = "ONLY_NEW"                      # Only cancel if order is new
    ONLY_PARTIALLY_FILLED = "ONLY_PARTIALLY_FILLED" # Only cancel if partially filled


@dataclass
class Fill:
    """Data structure for order fill information"""
    price: float
    qty: float
    commission: float
    commissionAsset: str
    tradeId: int
    
    @classmethod
    def from_api_response(cls, fill_data: Dict[str, Any]) -> 'Fill':
        return cls(
            price=float(fill_data['price']),
            qty=float(fill_data['qty']),
            commission=float(fill_data['commission']),
            commissionAsset=fill_data['commissionAsset'],
            tradeId=int(fill_data['tradeId'])
        )


@dataclass
class OrderResponseFull:
    """Full order response with fills information"""
    symbol: str
    orderId: int
    orderListId: int
    clientOrderId: str
    transactTime: int
    price: float
    origQty: float
    executedQty: float
    cummulativeQuoteQty: float
    status: OrderStatus
    timeInForce: TimeInForce
    type: OrderType
    side: OrderSide
    fills: List[Fill]
    workingTime: int = 0
    selfTradePreventionMode: str = "NONE"
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OrderResponseFull':
        fills = []
        if 'fills' in response:
            fills = [Fill.from_api_response(fill) for fill in response['fills']]
            
        return cls(
            symbol=response.get('symbol', ''),
            orderId=int(response.get('orderId', 0)),
            orderListId=int(response.get('orderListId', -1)),
            clientOrderId=response.get('clientOrderId', ''),
            transactTime=int(response.get('transactTime', 0)),
            price=float(response.get('price', 0)),
            origQty=float(response.get('origQty', 0)),
            executedQty=float(response.get('executedQty', 0)),
            cummulativeQuoteQty=float(response.get('cummulativeQuoteQty', 0)),
            status=OrderStatus(response.get('status', 'NEW')),
            timeInForce=TimeInForce(response.get('timeInForce', 'GTC')),
            type=OrderType(response.get('type', 'LIMIT')),
            side=OrderSide(response.get('side', 'BUY')),
            fills=fills,
            workingTime=int(response.get('workingTime', 0)),
            selfTradePreventionMode=response.get('selfTradePreventionMode', 'NONE')
        )


@dataclass
class OrderResponseResult:
    """Result-level order response without fills"""
    symbol: str
    orderId: int
    orderListId: int
    clientOrderId: str
    transactTime: int
    price: float
    origQty: float
    executedQty: float
    cummulativeQuoteQty: float
    status: OrderStatus
    timeInForce: TimeInForce
    type: OrderType
    side: OrderSide
    workingTime: int = 0
    selfTradePreventionMode: str = "NONE"
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OrderResponseResult':
        return cls(
            symbol=response.get('symbol', ''),
            orderId=int(response.get('orderId', 0)),
            orderListId=int(response.get('orderListId', -1)),
            clientOrderId=response.get('clientOrderId', ''),
            transactTime=int(response.get('transactTime', 0)),
            price=float(response.get('price', 0)),
            origQty=float(response.get('origQty', 0)),
            executedQty=float(response.get('executedQty', 0)),
            cummulativeQuoteQty=float(response.get('cummulativeQuoteQty', 0)),
            status=OrderStatus(response.get('status', 'NEW')),
            timeInForce=TimeInForce(response.get('timeInForce', 'GTC')),
            type=OrderType(response.get('type', 'LIMIT')),
            side=OrderSide(response.get('side', 'BUY')),
            workingTime=int(response.get('workingTime', 0)),
            selfTradePreventionMode=response.get('selfTradePreventionMode', 'NONE')
        )


@dataclass
class OrderResponseAck:
    """Simple acknowledgment response for orders"""
    symbol: str
    orderId: int
    orderListId: int
    clientOrderId: str
    transactTime: int
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OrderResponseAck':
        return cls(
            symbol=response.get('symbol', ''),
            orderId=int(response.get('orderId', 0)),
            orderListId=int(response.get('orderListId', -1)),
            clientOrderId=response.get('clientOrderId', ''),
            transactTime=int(response.get('transactTime', 0))
        )


@dataclass
class CancelReplaceResponse:
    """Response for cancel-replace operations"""
    cancelResult: str
    newOrderResult: str
    cancelResponse: Dict[str, Any]
    newOrderResponse: Dict[str, Any]
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'CancelReplaceResponse':
        return cls(
            cancelResult=response.get('cancelResult', ''),
            newOrderResult=response.get('newOrderResult', ''),
            cancelResponse=response.get('cancelResponse', {}),
            newOrderResponse=response.get('newOrderResponse', {})
        )


@dataclass
class OrderTrade:
    """Data structure for trade information specific to orders"""
    id: int
    orderId: int
    orderListId: int
    price: float
    qty: float
    quoteQty: float
    commission: float
    commissionAsset: str
    time: int
    isBuyer: bool
    isMaker: bool
    isBestMatch: bool
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OrderTrade':
        return cls(
            id=int(response['id']),
            orderId=int(response.get('orderId', 0)),
            orderListId=int(response.get('orderListId', -1)),
            price=float(response['price']),
            qty=float(response['qty']),
            quoteQty=float(response['quoteQty']),
            commission=float(response['commission']),
            commissionAsset=response['commissionAsset'],
            time=int(response['time']),
            isBuyer=bool(response['isBuyer']),
            isMaker=bool(response['isMaker']),
            isBestMatch=bool(response.get('isBestMatch', True))
        )


@dataclass
class PreventedMatch:
    """Data structure for self-trade prevention match information"""
    symbol: str
    preventedMatchId: int
    takerOrderId: int
    makerOrderId: int
    tradeGroupId: int
    selfTradePreventionMode: str
    price: float
    makerPreventedQuantity: float
    transactTime: int
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'PreventedMatch':
        return cls(
            symbol=response['symbol'],
            preventedMatchId=int(response['preventedMatchId']),
            takerOrderId=int(response['takerOrderId']),
            makerOrderId=int(response['makerOrderId']),
            tradeGroupId=int(response['tradeGroupId']),
            selfTradePreventionMode=response['selfTradePreventionMode'],
            price=float(response['price']),
            makerPreventedQuantity=float(response['makerPreventedQuantity']),
            transactTime=int(response['transactTime'])
        )


@dataclass
class RateLimitInfo:
    """Data structure for order rate limit information"""
    rateLimitType: str
    interval: str
    intervalNum: int
    limit: int
    count: int
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'RateLimitInfo':
        return cls(
            rateLimitType=response['rateLimitType'],
            interval=response['interval'],
            intervalNum=int(response['intervalNum']),
            limit=int(response['limit']),
            count=int(response['count'])
        )