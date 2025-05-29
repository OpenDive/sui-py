"""
Coin Query API client for Sui blockchain.

Implements all coin-related RPC methods from the Sui JSON-RPC API.
"""

from typing import Any, Dict, List, Optional
import re

from .rest_client import RestClient
from ..exceptions import SuiValidationError


class CoinQueryClient:
    """
    Client for Sui Coin Query API operations.
    
    Provides methods for querying coin balances, metadata, and ownership information.
    All methods return raw dictionary responses from the Sui JSON-RPC API.
    """
    
    def __init__(self, rest_client: RestClient):
        """
        Initialize the Coin Query client.
        
        Args:
            rest_client: The underlying REST client for making RPC calls
        """
        self.rest_client = rest_client
    
    @staticmethod
    def _validate_address(address: str) -> None:
        """
        Validate a Sui address format.
        
        Args:
            address: The address string to validate
            
        Raises:
            SuiValidationError: If the address format is invalid
        """
        if not isinstance(address, str):
            raise SuiValidationError("Address must be a string")
        
        # Sui addresses are 32-byte hex strings with 0x prefix
        if not re.match(r"^0x[a-fA-F0-9]{64}$", address):
            raise SuiValidationError(
                f"Invalid Sui address format: {address}. "
                "Expected 32-byte hex string with 0x prefix (66 characters total)"
            )
    
    @staticmethod
    def _validate_coin_type(coin_type: str) -> None:
        """
        Validate a coin type format.
        
        Args:
            coin_type: The coin type string to validate
            
        Raises:
            SuiValidationError: If the coin type format is invalid
        """
        if not isinstance(coin_type, str):
            raise SuiValidationError("Coin type must be a string")
        
        # Basic validation for coin type format (package::module::type)
        if not re.match(r"^0x[a-fA-F0-9]+::[a-zA-Z_][a-zA-Z0-9_]*::[a-zA-Z_][a-zA-Z0-9_]*$", coin_type):
            raise SuiValidationError(
                f"Invalid coin type format: {coin_type}. "
                "Expected format: 0x<package>::<module>::<type>"
            )
    
    async def get_all_balances(self, owner: str) -> List[Dict[str, Any]]:
        """
        Return the total coin balance for all coin types owned by the address.
        
        Args:
            owner: The owner's Sui address
            
        Returns:
            List of balance objects, each containing:
            - coinType: The coin type identifier
            - coinObjectCount: Number of coin objects
            - totalBalance: Total balance as string
            - lockedBalance: Locked balance information
            
        Raises:
            SuiValidationError: If the owner address is invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_address(owner)
        return await self.rest_client.call("suix_getAllBalances", [owner])
    
    async def get_all_coins(
        self, 
        owner: str, 
        cursor: Optional[str] = None, 
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Return all Coin objects owned by an address.
        
        Args:
            owner: The owner's Sui address
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            
        Returns:
            Dictionary containing:
            - data: List of coin objects
            - hasNextPage: Boolean indicating if more pages exist
            - nextCursor: Cursor for the next page (if hasNextPage is true)
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_address(owner)
        
        params = [owner]
        if cursor is not None:
            params.append(cursor)
            if limit is not None:
                params.append(limit)
        elif limit is not None:
            params.append(None)  # cursor placeholder
            params.append(limit)
        
        return await self.rest_client.call("suix_getAllCoins", params)
    
    async def get_balance(
        self, 
        owner: str, 
        coin_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Return the balance for a specific coin type owned by an address.
        
        Args:
            owner: The owner's Sui address
            coin_type: The coin type to query (defaults to SUI if not provided)
            
        Returns:
            Balance object containing:
            - coinType: The coin type identifier
            - coinObjectCount: Number of coin objects
            - totalBalance: Total balance as string
            - lockedBalance: Locked balance information
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_address(owner)
        
        params = [owner]
        if coin_type is not None:
            self._validate_coin_type(coin_type)
            params.append(coin_type)
        
        return await self.rest_client.call("suix_getBalance", params)
    
    async def get_coin_metadata(self, coin_type: str) -> Dict[str, Any]:
        """
        Return metadata for a coin type.
        
        Args:
            coin_type: The coin type to get metadata for
            
        Returns:
            Coin metadata object containing:
            - decimals: Number of decimal places
            - name: Coin name
            - symbol: Coin symbol
            - description: Coin description
            - iconUrl: URL to coin icon (if available)
            - id: Metadata object ID
            
        Raises:
            SuiValidationError: If the coin type is invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_coin_type(coin_type)
        return await self.rest_client.call("suix_getCoinMetadata", [coin_type])
    
    async def get_coins(
        self,
        owner: str,
        coin_type: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Return coins of a specific type owned by an address.
        
        Args:
            owner: The owner's Sui address
            coin_type: The coin type to query (defaults to SUI if not provided)
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            
        Returns:
            Dictionary containing:
            - data: List of coin objects
            - hasNextPage: Boolean indicating if more pages exist
            - nextCursor: Cursor for the next page (if hasNextPage is true)
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_address(owner)
        
        params = [owner]
        if coin_type is not None:
            self._validate_coin_type(coin_type)
            params.append(coin_type)
            
        if cursor is not None:
            if coin_type is None:
                params.append(None)  # coin_type placeholder
            params.append(cursor)
            
        if limit is not None:
            if coin_type is None:
                if cursor is None:
                    params.extend([None, None])  # coin_type and cursor placeholders
                else:
                    params.insert(-1, None)  # coin_type placeholder before cursor
            elif cursor is None:
                params.append(None)  # cursor placeholder
            params.append(limit)
        
        return await self.rest_client.call("suix_getCoins", params)
    
    async def get_total_supply(self, coin_type: str) -> Dict[str, Any]:
        """
        Return the total supply for a coin type.
        
        Args:
            coin_type: The coin type to get total supply for
            
        Returns:
            Supply object containing:
            - value: Total supply as string
            
        Raises:
            SuiValidationError: If the coin type is invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_coin_type(coin_type)
        return await self.rest_client.call("suix_getTotalSupply", [coin_type]) 