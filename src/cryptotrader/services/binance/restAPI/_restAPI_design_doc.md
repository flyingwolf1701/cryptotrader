Binance API Client Development Guidelines
Project Structure
The Binance API implementation follows a well-defined folder structure:
```bash
src/cryptotrader/services/binance/
├── __init__.py                # Main package exports
├── models/                    # Data models
│   ├── __init__.py            # Exports all models
│   ├── base_models.py         # Core models used across APIs
│   ├── order_models.py        # Order-specific models
│   ├── market_models.py       # Market data models
│   ├── user_models.py         # User account models
│   ├── wallet_models.py       # Wallet operation models
│   ├── otc_models.py          # OTC trading models
│   └── staking_models.py      # Staking operation models
├── restAPI/                   # REST API implementation
│   ├── __init__.py            # Exports clients
│   ├── base_operations.py     # Core request functionality
│   ├── system_api.py          # System information operations
│   ├── market_api.py          # Market data operations
│   ├── order_api.py           # Order operations
│   ├── user_api.py            # User account operations
│   ├── wallet_api.py          # Wallet operations
│   ├── subaccount_api.py      # Sub-account management
│   ├── otc_api.py             # OTC trading operations
│   └── staking_api.py         # Staking operations
├── diagnostic_scripts/        # Diagnostic/testing scripts
│   ├── system_diagnostic.py   # Tests system API functionality
│   ├── market_diagnostic.py   # Tests market API functionality
│   ├── order_diagnostic.py    # Tests order API functionality
│   ├── user_diagnostic.py     # Tests user API functionality
│   ├── wallet_diagnostic.py   # Tests wallet API functionality
│   ├── subaccount_diagnostic.py # Tests sub-account functionality
│   ├── otc_diagnostic.py      # Tests OTC API functionality
│   └── staking_diagnostic.py  # Tests staking functionality
└── websocketAPI/              # WebSocket API (covered separately)
```
Each functional area of the Binance API should have three corresponding components:

A models file in the models/ directory
An API implementation in the restAPI/ directory
A diagnostic script in the diagnostic_scripts/ directory

Architecture Overview
When creating new API endpoints for the Binance API client, follow these architectural patterns to ensure consistency across the codebase:
1. Base Operations Architecture
The BinanceAPIRequest class in base_operations.py serves as the foundation for all API requests:

It handles authentication by retrieving API credentials from Secrets
It manages rate limiting
It handles request signing for authenticated endpoints
It provides retry logic and error handling

2. Implementation Pattern for API Clients
When implementing a new API client module (e.g., for a specific group of API endpoints):
API Class Structure:
```python
class NewAPIOperations:
    """
    Binance [Category] API client implementation.
    
    Provides methods for [brief description of functionality].
    """
    
    def __init__(self):
        """Initialize the client."""
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
        
    # API endpoint methods follow with actual endpoint paths in comments
    
    def get_endpoint_data(self, symbol: str) -> ReturnType:
        """
        Description of what this endpoint does.
        
        GET /api/v3/endpoint
        Weight: X
        
        Args:
            symbol: Description of parameter
            
        Returns:
            Description of return value
        """
        # Implementation...
```
Endpoint Method Pattern:
```python
def endpoint_method(self, required_param: str, optional_param: Optional[int] = None) -> ReturnType:
    """
    Description of what this endpoint does.
    
    GET /api/v3/specific-endpoint
    Weight: X
    
    Args:
        required_param: Description of parameter
        optional_param: Description of optional parameter
        
    Returns:
        Description of return value
    """
    request = self.request("METHOD", "/api/v3/specific-endpoint", RateLimitType.REQUEST_WEIGHT, weight) \
        .requires_auth(True/False) \
        .with_query_params(param=required_param)
        
    if optional_param is not None:
        request.with_query_params(optionalParam=optional_param)
        
    response = request.execute()
    
    if response:
        # Transform response into return type
        return transformed_response
    return None  # or empty list/default value
```
Models Architecture
The project uses a layered model architecture to represent API data:
Base Models
base_models.py contains fundamental data structures used across all API endpoints:

Enumerations for common constants (e.g., OrderType, OrderSide, TimeInForce)
Core data classes (e.g., SystemStatus, RateLimit)
Utility models used across multiple API areas (e.g., PriceData, Candle)

```python
# Example from base_models.py
@dataclass
class SystemStatus:
    """System status information"""
    status_code: int  # 0: normal, 1: system maintenance, -1: unknown
    
    @property
    def is_normal(self) -> bool:
        """Check if system status is normal"""
        return self.status_code == 0
```
Feature-Specific Models
Each API area should have its own models file (e.g., order_models.py, market_models.py):

Models should match the corresponding API implementation (e.g., order_api.py → order_models.py)
These files contain models specific to that API area
They can reference and build upon base models

```python
# Example from order_models.py
@dataclass
class OrderResponseFull:
    """Full order response with fills information"""
    symbol: str
    orderId: int
    # ... other fields ...
    status: OrderStatus  # Referencing enum from base_models
    timeInForce: TimeInForce  # Referencing enum from base_models
    type: OrderType  # Referencing enum from base_models
    side: OrderSide  # Referencing enum from base_models
    fills: List[Fill]  # Referencing another model
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OrderResponseFull':
        """Factory method to create from API response"""
        # ... implementation ...
```
Model Best Practices

Use Data Classes: Leverage Python's @dataclass decorator for all models
Factory Methods: Include from_api_response() class methods to create models from API responses
Type Safety: Use proper type annotations including generics for containers
Documentation: Include docstrings for classes and complex properties
Property Methods: Use @property for derived values or convenience accessors
Field Naming: Match Binance API field names in the models to simplify mapping
Inheritance: Use inheritance when appropriate (e.g., PriceStats extends PriceStatsMini)

Integration with API Implementation
API methods should return properly typed models rather than raw dictionaries:
```python
def get_order_status(self, symbol: str, order_id: int) -> Optional[OrderStatusResponse]:
    # ... implementation ...
    response = request.execute()
    
    if response:
        return OrderStatusResponse.from_api_response(response)
    return None
```
Key Guidelines

Authentication Handling:

Never pass API credentials to the client class constructor
Let BinanceAPIRequest handle authentication via Secrets.BINANCE_API_KEY and Secrets.BINANCE_API_SECRET
Use .requires_auth(True) for endpoints requiring authentication
Use .requires_auth(False) for public endpoints that don't need authentication
The requires_auth() method will:

Add a timestamp to the request parameters
Create an HMAC-SHA256 signature using the secret key
Add the signature to the request parameters
Add the API key to the request headers




Rate Limiting:

Always specify the correct weight for each endpoint
Use appropriate RateLimitType for each request


Parameter Handling:

Validate parameters before sending (e.g., ensure limits don't exceed API maximums)
Use snake_case for method parameters
Use camelCase when passing to the API via with_query_params()


Response Handling:

Always handle the case where the API returns None or an error
Use model classes from models.py to transform API responses into typed objects
For list responses, return an empty list rather than None when appropriate


Documentation:

Include comprehensive docstrings for all methods
Always document the API weight
Clearly describe parameters and return values
Note any special behavior or requirements
Include the actual API endpoint path in the docstring



Diagnostic Scripts
Diagnostic scripts provide a way to test API functionality without integrating it into the main application. Each API area should have a corresponding diagnostic script:
Diagnostic Script Structure
```python
"""
Binance [Feature] API Diagnostic Script
---------------------------------------
Tests the Binance [Feature] API client to verify functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/[feature]_diagnostic.py
"""

import sys
from pathlib import Path
import traceback
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.models import (
    # Import relevant models...
)

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing

def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")

def main():
    logger.info(f"Added {project_root} to Python path")
    
    logger.info("Initializing Binance client...")
    client = Client()  # No need to pass API credentials
    
    # Test 1: Test basic functionality
    print_test_header("Basic Functionality Test")
    try:
        # Test implementation...
        logger.info("Test passed!")
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Additional tests...
    
    # Summary
    logger.info("\nDiagnostic Summary:")
    logger.info("----------------------------")
    # Summary information...
    
    logger.info("\nDiagnostic completed.")

if __name__ == "__main__":
    main()
```
Diagnostic Best Practices

Colorful Output: Use colorama to make output more readable with color-coded sections
Safe Testing: Design tests to be read-only when possible, or clearly indicate when they're not
Comprehensive Coverage: Test all key functionality in the corresponding API
Error Handling: Wrap each test in try/except blocks to prevent early termination
Detailed Logging: Log detailed information about what's being tested and the results
Clear Headers: Use the print_test_header function to clearly separate test sections
Fallbacks: Include graceful fallbacks when API keys aren't available
Summary: Provide a summary of all test results at the end

Example Diagnostic Script: order_diagnostic.py
Here's a specific example from the order_diagnostic.py script that demonstrates how to create an effective diagnostic:
```python
# Test 1: Get account balance
print_test_header("Getting Account Balance")
try:
    balance = client.get_balance()
    if balance and balance.assets:
        logger.info("Account balance retrieved successfully")
        # Print assets with non-zero balances
        non_zero_assets = {asset: data for asset, data in balance.assets.items() 
                        if float(data.free) > 0 or float(data.locked) > 0}
        
        if non_zero_assets:
            logger.info("Assets with non-zero balance:")
            for asset, data in non_zero_assets.items():
                logger.info(f"  {asset}: Free={data.free}, Locked={data.locked}")
        else:
            logger.info("No assets with non-zero balance found")
    else:
        logger.warning("No balance data retrieved or empty response")
except Exception as e:
    logger.error(f"Error retrieving account balance: {str(e)}")
    logger.debug(traceback.format_exc())
```
Key features of this diagnostic test:

Clear test header using colorama
Comprehensive error handling
Detailed output formatting
Conditional logic to handle various response scenarios
Appropriate logging levels for different information

Authentication Flow in Detail
The authentication process is handled by BinanceAPIRequest in these steps:

When you call .requires_auth(True) on a request:
pythonrequest = self.request("GET", "/api/v3/endpoint").requires_auth(True)

BinanceAPIRequest internally sets self.needs_signature = True which will trigger signature generation on execution
During execute(), if authentication is needed, the sign_request() method is called which:

Adds the current timestamp: self.params['timestamp'] = str(int(time.time() * 1000))
Creates a query string from all parameters
Creates an HMAC-SHA256 signature using the secret key from Secrets.BINANCE_API_SECRET
Adds the signature to params: self.params['signature'] = signature


The API key from Secrets.BINANCE_API_KEY is added to the request headers:
pythonheaders['X-MBX-APIKEY'] = self.public_key

The request is then executed with these authentication credentials

This ensures all authentication is handled consistently throughout the codebase, with no need to implement it in individual API client classes.
Example Implementation
```python
from typing import Dict, List, Optional, Any

from cryptotrader.config import get_logger
from src.cryptotrader.services.binance.restAPI.base_operations import BinanceAPIRequest
from cryptotrader.services.binance.models import RateLimitType, SomeResponseModel

logger = get_logger(__name__)

class ExampleOperations:
    def __init__(self):
        """Initialize the Example API client."""
        pass
    
    def request(self, method: str, endpoint: str, 
               limit_type: Optional[RateLimitType] = None,
               weight: int = 1) -> BinanceAPIRequest:
        """Create a new API request."""
        return BinanceAPIRequest(
            method=method, 
            endpoint=endpoint,
            limit_type=limit_type,
            weight=weight
        )
    
    def get_example_data(self, symbol: str, limit: int = 100) -> Optional[SomeResponseModel]:
        """
        Get example data for a symbol.
        
        GET /api/v3/example-data
        Weight: 1
        
        Args:
            symbol: Symbol to get data for (e.g. "BTCUSDT")
            limit: Number of records to return (default 100, max 500)
            
        Returns:
            SomeResponseModel object with retrieved data, or None if request fails
        """
        response = self.request("GET", "/api/v3/example-data", RateLimitType.REQUEST_WEIGHT, 1) \
            .requires_auth(False) \
            .with_query_params(
                symbol=symbol,
                limit=min(limit, 500)  # Ensure limit doesn't exceed API max
            ) \
            .execute()
            
        if response is not None:
            return SomeResponseModel.from_api_response(response)
        
        return None
```
Updating __init__.py Files
When adding a new API feature, you must update the appropriate __init__.py files to export your models and API classes. When exporting API functions, include the actual endpoint path as a comment:
```python
"""
Binance API Module

This module provides a comprehensive client for interacting with the Binance API,
including market data, trading operations, and system information.
"""

# Import client classes
from .general_api import RestClient as Client
from .base_operations import BinanceAPIRequest
from .order_api import OrderOperations

# Export functions with their endpoint paths in comments
__all__ = [
    # Client classes
    'Client',
    'BinanceAPIRequest',
    'OrderOperations',
    
    # API Functions
    'get_balance',           # GET /api/v3/account
    'get_order_status',      # GET /api/v3/order
    'place_order',           # POST /api/v3/order
    'cancel_order',          # DELETE /api/v3/order
    'get_open_orders',       # GET /api/v3/openOrders
    'get_all_orders',        # GET /api/v3/allOrders
    'get_server_time',       # GET /api/v3/time
    'get_ticker_price',      # GET /api/v3/ticker/price
    'get_24h_stats',         # GET /api/v3/ticker/24hr
]
```
This approach makes it easy to identify which API endpoints correspond to which exported functions, especially for developers who are new to the codebase or the Binance API.
Creating a New Feature: Complete Process
When adding a new API feature, follow this complete process:

Create Models: Add new models to an existing or new models file
Implement API: Create or update an API implementation file
Create Diagnostic: Build a diagnostic script to test the new functionality
Update init.py: Export new models and API classes in the appropriate init.py files with endpoint comments
Documentation: Ensure all components are properly documented
Test: Run the diagnostic script to verify functionality

By following these guidelines, you'll ensure that all API clients maintain a consistent structure, making the codebase more maintainable and reducing the chance of bugs related to authentication or rate limiting.