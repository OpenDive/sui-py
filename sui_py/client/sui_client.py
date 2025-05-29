"""
Main Sui client that provides access to all Sui blockchain APIs.
"""

from typing import Optional, Union

from .rest_client import RestClient
from .coin_query import CoinQueryClient
from ..constants import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES, DEFAULT_RETRY_DELAY


class SuiClient:
    """
    Main async client for interacting with the Sui blockchain.
    
    Provides access to all Sui JSON-RPC APIs through specialized sub-clients.
    Designed for async/await usage with proper resource management.
    
    Example:
        async with SuiClient("mainnet") as client:
            balance = await client.coin_query.get_balance(address)
            coins = await client.coin_query.get_all_coins(address)
    """
    
    def __init__(
        self,
        network_or_endpoint: str,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ):
        """
        Initialize the Sui client.
        
        Args:
            network_or_endpoint: Network name (mainnet, testnet, devnet, localnet) 
                                or custom RPC endpoint URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        # Determine if this is a network name or custom endpoint
        if network_or_endpoint.startswith(("http://", "https://")):
            # Custom endpoint
            self._rest_client = RestClient(
                endpoint=network_or_endpoint,
                timeout=timeout,
                max_retries=max_retries,
                retry_delay=retry_delay
            )
        else:
            # Network name
            self._rest_client = RestClient.from_network(
                network=network_or_endpoint,
                timeout=timeout,
                max_retries=max_retries,
                retry_delay=retry_delay
            )
        
        # Initialize API clients
        self.coin_query = CoinQueryClient(self._rest_client)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._rest_client.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._rest_client.close()
    
    async def connect(self) -> None:
        """
        Manually connect the client.
        
        Note: It's recommended to use the async context manager instead.
        """
        await self._rest_client.connect()
    
    async def close(self) -> None:
        """
        Manually close the client.
        
        Note: It's recommended to use the async context manager instead.
        """
        await self._rest_client.close()
    
    @property
    def endpoint(self) -> str:
        """Get the current RPC endpoint."""
        return self._rest_client.endpoint
    
    @property
    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self._rest_client._client is not None 