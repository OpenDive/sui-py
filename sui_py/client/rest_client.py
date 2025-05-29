"""
Core REST client for JSON-RPC communication with Sui nodes.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
import httpx

from ..constants import (
    NETWORK_ENDPOINTS, 
    DEFAULT_TIMEOUT, 
    DEFAULT_MAX_RETRIES, 
    DEFAULT_RETRY_DELAY,
    JSONRPC_VERSION
)
from ..exceptions import SuiRPCError, SuiNetworkError, SuiTimeoutError, SuiValidationError


class RestClient:
    """
    Async REST client for JSON-RPC communication with Sui nodes.
    
    Handles request/response formatting, error handling, and retries.
    """
    
    def __init__(
        self,
        endpoint: str,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ):
        """
        Initialize the REST client.
        
        Args:
            endpoint: The RPC endpoint URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Optional[httpx.AsyncClient] = None
        self._request_id = 0
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self) -> None:
        """Initialize the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={"Content-Type": "application/json"}
            )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _get_next_request_id(self) -> int:
        """Get the next request ID."""
        self._request_id += 1
        return self._request_id
    
    def _build_request(self, method: str, params: List[Any]) -> Dict[str, Any]:
        """
        Build a JSON-RPC request.
        
        Args:
            method: The RPC method name
            params: List of parameters
            
        Returns:
            JSON-RPC request dictionary
        """
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": self._get_next_request_id(),
            "method": method,
            "params": params
        }
    
    def _handle_response(self, response_data: Dict[str, Any]) -> Any:
        """
        Handle JSON-RPC response and extract result or raise error.
        
        Args:
            response_data: The JSON-RPC response
            
        Returns:
            The result data
            
        Raises:
            SuiRPCError: If the response contains an error
        """
        if "error" in response_data:
            error = response_data["error"]
            raise SuiRPCError(
                message=error.get("message", "Unknown RPC error"),
                code=error.get("code"),
                data=error.get("data")
            )
        
        if "result" not in response_data:
            raise SuiRPCError("Invalid response: missing result field")
        
        return response_data["result"]
    
    async def _make_request_with_retry(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            request_data: The JSON-RPC request data
            
        Returns:
            The response data
            
        Raises:
            SuiNetworkError: For network-related errors
            SuiTimeoutError: For timeout errors
        """
        if not self._client:
            raise SuiNetworkError("Client not connected. Use async context manager or call connect().")
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.post(
                    self.endpoint,
                    json=request_data
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.TimeoutException as e:
                last_exception = SuiTimeoutError(f"Request timed out after {self.timeout}s")
                
            except httpx.HTTPStatusError as e:
                last_exception = SuiNetworkError(f"HTTP {e.response.status_code}: {e.response.text}")
                
            except httpx.RequestError as e:
                last_exception = SuiNetworkError(f"Network error: {str(e)}")
                
            except json.JSONDecodeError as e:
                last_exception = SuiNetworkError(f"Invalid JSON response: {str(e)}")
            
            # If this wasn't the last attempt, wait before retrying
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
        # All retries failed
        raise last_exception
    
    async def call(self, method: str, params: Optional[List[Any]] = None) -> Any:
        """
        Make a JSON-RPC call to the Sui node.
        
        Args:
            method: The RPC method name
            params: List of parameters (optional)
            
        Returns:
            The result from the RPC call
            
        Raises:
            SuiRPCError: For RPC-level errors
            SuiNetworkError: For network-related errors
            SuiTimeoutError: For timeout errors
        """
        if params is None:
            params = []
        
        request_data = self._build_request(method, params)
        response_data = await self._make_request_with_retry(request_data)
        return self._handle_response(response_data)
    
    @classmethod
    def from_network(
        cls, 
        network: str,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ) -> "RestClient":
        """
        Create a REST client for a specific network.
        
        Args:
            network: Network name (mainnet, testnet, devnet, localnet)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            RestClient instance
            
        Raises:
            SuiValidationError: If network is not supported
        """
        if network not in NETWORK_ENDPOINTS:
            raise SuiValidationError(
                f"Unsupported network: {network}. "
                f"Supported networks: {list(NETWORK_ENDPOINTS.keys())}"
            )
        
        endpoint = NETWORK_ENDPOINTS[network]
        return cls(endpoint, timeout, max_retries, retry_delay) 