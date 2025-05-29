"""
Coin Query API client for Sui blockchain.

Implements all coin-related RPC methods from the Sui JSON-RPC API.
"""

from typing import Any, Dict, List, Optional, Union
import re

from .rest_client import RestClient
from ..exceptions import SuiValidationError
from ..types import Balance, Coin, SuiCoinMetadata, Supply, Page, SuiAddress


class CoinQueryClient:
    """
    Client for Sui Coin Query API operations.
    
    Provides methods for querying coin balances, metadata, and ownership information.
    All methods return typed objects corresponding to the Sui JSON-RPC API schemas.
    """
    
    def __init__(self, rest_client: RestClient):
        """
        Initialize the Coin Query client.
        
        Args:
            rest_client: The underlying REST client for making RPC calls
        """
        self.rest_client = rest_client
    
    @staticmethod
    def _validate_address(address: Union[str, SuiAddress]) -> str:
        """
        Validate and normalize a Sui address.
        
        Args:
            address: The address string or SuiAddress to validate
            
        Returns:
            The normalized address string
            
        Raises:
            SuiValidationError: If the address format is invalid
        """
        if isinstance(address, SuiAddress):
            return str(address)
        
        if not isinstance(address, str):
            raise SuiValidationError("Address must be a string or SuiAddress")
        
        # Validate using SuiAddress constructor
        validated_address = SuiAddress.from_str(address)
        return str(validated_address)
    
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
    
    async def get_all_balances(self, owner: Union[str, SuiAddress]) -> List[Balance]:
        """
        Return the total coin balance for all coin types owned by the address.
        
        Args:
            owner: The owner's Sui address
            
        Returns:
            List of Balance objects
            
        Raises:
            SuiValidationError: If the owner address is invalid
            SuiRPCError: If the RPC call fails
        """
        owner_str = self._validate_address(owner)
        response = await self.rest_client.call("suix_getAllBalances", [owner_str])
        return [Balance.from_dict(balance_data) for balance_data in response]
    
    async def get_all_coins(
        self, 
        owner: Union[str, SuiAddress], 
        cursor: Optional[str] = None, 
        limit: Optional[int] = None
    ) -> Page[Coin]:
        """
        Return all Coin objects owned by an address.
        
        Args:
            owner: The owner's Sui address
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            
        Returns:
            Page of Coin objects
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        owner_str = self._validate_address(owner)
        
        params = [owner_str]
        if cursor is not None:
            params.append(cursor)
            if limit is not None:
                params.append(limit)
        elif limit is not None:
            params.append(None)  # cursor placeholder
            params.append(limit)
        
        response = await self.rest_client.call("suix_getAllCoins", params)
        return Page.from_dict(response, Coin.from_dict)
    
    async def get_balance(
        self, 
        owner: Union[str, SuiAddress], 
        coin_type: Optional[str] = None
    ) -> Balance:
        """
        Return the balance for a specific coin type owned by an address.
        
        Args:
            owner: The owner's Sui address
            coin_type: The coin type to query (defaults to SUI if not provided)
            
        Returns:
            Balance object
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        owner_str = self._validate_address(owner)
        
        params = [owner_str]
        if coin_type is not None:
            self._validate_coin_type(coin_type)
            params.append(coin_type)
        
        response = await self.rest_client.call("suix_getBalance", params)
        return Balance.from_dict(response)
    
    async def get_coin_metadata(self, coin_type: str) -> SuiCoinMetadata:
        """
        Return metadata for a coin type.
        
        Args:
            coin_type: The coin type to get metadata for
            
        Returns:
            SuiCoinMetadata object
            
        Raises:
            SuiValidationError: If the coin type is invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_coin_type(coin_type)
        response = await self.rest_client.call("suix_getCoinMetadata", [coin_type])
        return SuiCoinMetadata.from_dict(response)
    
    async def get_coins(
        self,
        owner: Union[str, SuiAddress],
        coin_type: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Page[Coin]:
        """
        Return coins of a specific type owned by an address.
        
        Args:
            owner: The owner's Sui address
            coin_type: The coin type to query (defaults to SUI if not provided)
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            
        Returns:
            Page of Coin objects
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        owner_str = self._validate_address(owner)
        
        params = [owner_str]
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
        
        response = await self.rest_client.call("suix_getCoins", params)
        return Page.from_dict(response, Coin.from_dict)
    
    async def get_total_supply(self, coin_type: str) -> Supply:
        """
        Return the total supply for a coin type.
        
        Args:
            coin_type: The coin type to get total supply for
            
        Returns:
            Supply object
            
        Raises:
            SuiValidationError: If the coin type is invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_coin_type(coin_type)
        response = await self.rest_client.call("suix_getTotalSupply", [coin_type])
        return Supply.from_dict(response) 