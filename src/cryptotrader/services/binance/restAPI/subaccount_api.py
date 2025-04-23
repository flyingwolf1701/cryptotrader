"""
Binance Sub-Account API Client

This module provides a client for interacting with the Binance sub-account API endpoints.
It includes functionality for:
- Sub-account information retrieval
- Sub-account transfer history
- Executing sub-account transfers
- Sub-account asset information
- Master account total value information
- Sub-account status list

These endpoints provide information and operations related to sub-accounts for
institutional or professional users who manage multiple accounts.
"""

from typing import Dict, List, Optional, Any, Union

from config import get_logger
from src.cryptotrader.services.binance.restAPI.base_operations import BinanceAPIRequest
from cryptotrader.services.binance.models import RateLimitType

logger = get_logger(__name__)

class SubAccountOperations:
    """
    Binance sub-account API client implementation.
    
    Provides methods for managing and retrieving information about sub-accounts.
    """
    
    def __init__(self):
        """Initialize the Sub-Account client."""
        pass
    
    def request(self, method: str, endpoint: str, 
               limit_type: Optional[RateLimitType] = None,
               weight: int = 1) -> BinanceAPIRequest:
        """
        Create a new API request.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            limit_type: Type of rate limit for this request
            weight: Weight of this request for rate limiting
            
        Returns:
            BinanceAPIRequest object for building and executing the request
        """
        return BinanceAPIRequest(
            method=method, 
            endpoint=endpoint,
            limit_type=limit_type,
            weight=weight
        )
    
    def get_subaccount_list(self, email: Optional[str] = None, 
                          status: Optional[str] = None,
                          page: Optional[int] = None,
                          limit: Optional[int] = None,
                          recv_window: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get sub-account list.
        
        GET /sapi/v3/sub-account/list
        Weight: 1
        
        Args:
            email: Sub-account email
            status: Sub-account status: enabled or disabled
            page: Page number, default value: 1
            limit: Results per page, default value: 500
            recv_window: The value cannot be greater than 60000
            
        Returns:
            Dictionary with sub-account list information
        """
        request = self.request("GET", "/sapi/v3/sub-account/list", weight=1).requires_auth(True)
        
        if email is not None:
            request.with_query_params(email=email)
        if status is not None:
            request.with_query_params(status=status)
        if page is not None:
            request.with_query_params(page=page)
        if limit is not None:
            request.with_query_params(limit=min(limit, 500))  # Ensure limit doesn't exceed API max
        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)
            
        response = request.execute()
        return response
    
    def get_subaccount_transfer_history(self, email: Optional[str] = None,
                                      start_time: Optional[int] = None,
                                      end_time: Optional[int] = None,
                                      page: Optional[int] = None,
                                      limit: Optional[int] = None,
                                      recv_window: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get sub-account transfer history.
        
        GET /sapi/v3/sub-account/transfer/history
        Weight: 1
        
        Args:
            email: Sub-account email
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            page: Page number (each page contains at most 500 transfer history records)
            limit: Results per page, default value: 500
            recv_window: The value cannot be greater than 60000
            
        Returns:
            Dictionary with sub-account transfer history information
        """
        request = self.request("GET", "/sapi/v3/sub-account/transfer/history", weight=1).requires_auth(True)
        
        if email is not None:
            request.with_query_params(email=email)
        if start_time is not None:
            request.with_query_params(startTime=start_time)
        if end_time is not None:
            request.with_query_params(endTime=end_time)
        if page is not None:
            request.with_query_params(page=page)
        if limit is not None:
            request.with_query_params(limit=min(limit, 500))  # Ensure limit doesn't exceed API max
        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)
            
        response = request.execute()
        return response
    
    def execute_subaccount_transfer(self, from_email: str, to_email: str, 
                                 asset: str, amount: Union[str, float],
                                 recv_window: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a sub-account transfer.
        
        POST /sapi/v3/sub-account/transfer
        Weight: 1
        
        Args:
            from_email: Sender email
            to_email: Recipient email
            asset: Asset to transfer
            amount: Amount to transfer
            recv_window: The value cannot be greater than 60000
            
        Returns:
            Dictionary with transfer execution information
        """
        request = self.request("POST", "/sapi/v3/sub-account/transfer", weight=1).requires_auth(True)
        
        # Required parameters
        request.with_query_params(
            fromEmail=from_email,
            toEmail=to_email,
            asset=asset,
            amount=str(amount)  # Ensure amount is a string
        )
        
        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)
            
        response = request.execute()
        return response
    
    def get_subaccount_assets(self, email: str, 
                           recv_window: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get sub-account assets.
        
        GET /sapi/v3/sub-account/assets
        Weight: 1
        
        Args:
            email: Sub-account email
            recv_window: The value cannot be greater than 60000
            
        Returns:
            Dictionary with sub-account assets information
        """
        request = self.request("GET", "/sapi/v3/sub-account/assets", weight=1).requires_auth(True)
        
        # Required parameters
        request.with_query_params(email=email)
        
        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)
            
        response = request.execute()
        return response
    
    def get_master_account_total_value(self, email: Optional[str] = None,
                                     page: Optional[int] = None, 
                                     size: Optional[int] = None,
                                     recv_window: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get master account's total USD value.
        
        GET /sapi/v1/sub-account/spotSummary
        Weight: 1
        
        Args:
            email: Sub-account email
            page: Page number
            size: Page size
            recv_window: The value cannot be greater than 60000
            
        Returns:
            Dictionary with master account total value information
        """
        request = self.request("GET", "/sapi/v1/sub-account/spotSummary", weight=1).requires_auth(True)
        
        if email is not None:
            request.with_query_params(email=email)
        if page is not None:
            request.with_query_params(page=page)
        if size is not None:
            request.with_query_params(size=size)
        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)
            
        response = request.execute()
        return response
    
    def get_subaccount_status_list(self, email: str,
                                recv_window: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Get sub-account status list.
        
        GET /sapi/v1/sub-account/status
        Weight: 1
        
        Args:
            email: Sub-account email
            recv_window: The value cannot be greater than 60000
            
        Returns:
            List of dictionaries with sub-account status information
        """
        request = self.request("GET", "/sapi/v1/sub-account/status", weight=1).requires_auth(True)
        
        # Required parameters
        request.with_query_params(email=email)
        
        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)
            
        response = request.execute()
        return response