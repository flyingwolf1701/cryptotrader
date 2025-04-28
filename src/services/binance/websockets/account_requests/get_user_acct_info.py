"""
Binance WebSocket API Account Information Request

This module provides functionality to retrieve account information via the Binance WebSocket API.
It follows the Binance WebSocket API specifications for the 'account.status' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.base_operations import BinanceWebSocketConnection, SecurityType
from services.binance.models import AccountBalance

logger = get_logger(__name__)

async def getAccountWS(
    connection: BinanceWebSocketConnection,
    recv_window: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve current account information.
    
    Gets detailed information about the user's account including balances,
    permissions, commissions, and account type.
    
    Endpoint: account.status
    Weight: 10
    Security Type: USER_DATA (Requires API key and signature)
    Data Source: Memory => Database
    
    Args:
        connection: Active WebSocket connection
        recv_window: Maximum time in milliseconds request is valid for (optional)
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If recv_window exceeds 60000
    """
    # Validate parameters
    if recv_window is not None:
        if not isinstance(recv_window, int) or recv_window <= 0:
            raise ValueError("recv_window must be a positive integer")
        if recv_window > 60000:
            raise ValueError("recv_window cannot exceed 60000")
    
    # Prepare request parameters
    params = {}
    if recv_window is not None:
        params["recvWindow"] = recv_window
    
    # Send the request with USER_DATA security type
    # This requires API key and signature which will be added automatically
    msg_id = await connection.send(
        method="account.status",
        params=params,
        security_type=SecurityType.USER_DATA
    )
    
    logger.debug(f"Sent account information request with ID: {msg_id}")
    return msg_id

async def process_account_info_response(response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process the account information response.
    
    Args:
        response: WebSocket response data
        
    Returns:
        Processed account information if successful, None otherwise
        
    The returned dictionary includes:
    - Commission rates
    - Account status flags (canTrade, canWithdraw, canDeposit)
    - Account balances
    - Account permissions
    - Account type
    - Update time
    """
    if not response or 'result' not in response:
        logger.error("Invalid account information response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        
        # Process and return account information
        account_info = {
            "makerCommission": result.get("makerCommission"),
            "takerCommission": result.get("takerCommission"),
            "buyerCommission": result.get("buyerCommission"),
            "sellerCommission": result.get("sellerCommission"),
            "canTrade": result.get("canTrade"),
            "canWithdraw": result.get("canWithdraw"),
            "canDeposit": result.get("canDeposit"),
            "commissionRates": result.get("commissionRates", {}),
            "brokered": result.get("brokered"),
            "requireSelfTradePrevention": result.get("requireSelfTradePrevention"),
            "updateTime": result.get("updateTime"),
            "accountType": result.get("accountType"),
            "permissions": result.get("permissions", []),
            "balances": AccountBalance.from_api_response(result)
        }
        
        return account_info
    except Exception as e:
        logger.error(f"Error processing account information response: {str(e)}")
        return None