"""
Extended API client for Sui blockchain.

Implements extended RPC methods from the Sui JSON-RPC API including:
- Dynamic field operations
- Object queries
- Event queries
- Transaction queries
- Name service resolution
- Subscription methods (note: subscriptions require WebSocket support)
"""

from typing import Any, Dict, List, Optional, Union
import re

from .rest_client import RestClient
from ..exceptions import SuiValidationError


class ExtendedAPIClient:
    """
    Client for Sui Extended API operations.
    
    Provides methods for querying objects, events, transactions, and dynamic fields.
    All methods return raw dictionary responses from the Sui JSON-RPC API.
    """
    
    def __init__(self, rest_client: RestClient):
        """
        Initialize the Extended API client.
        
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
    def _validate_object_id(object_id: str) -> None:
        """
        Validate a Sui object ID format.
        
        Args:
            object_id: The object ID string to validate
            
        Raises:
            SuiValidationError: If the object ID format is invalid
        """
        if not isinstance(object_id, str):
            raise SuiValidationError("Object ID must be a string")
        
        # Object IDs are 32-byte hex strings with 0x prefix
        if not re.match(r"^0x[a-fA-F0-9]{64}$", object_id):
            raise SuiValidationError(
                f"Invalid object ID format: {object_id}. "
                "Expected 32-byte hex string with 0x prefix (66 characters total)"
            )
    
    @staticmethod
    def _validate_transaction_digest(digest: str) -> None:
        """
        Validate a transaction digest format.
        
        Args:
            digest: The transaction digest string to validate
            
        Raises:
            SuiValidationError: If the digest format is invalid
        """
        if not isinstance(digest, str):
            raise SuiValidationError("Transaction digest must be a string")
        
        # Transaction digests are base58 encoded strings
        # Basic length check (typically 43-44 characters for base58)
        if len(digest) < 40 or len(digest) > 50:
            raise SuiValidationError(
                f"Invalid transaction digest format: {digest}. "
                "Expected base58 encoded string"
            )
    
    async def get_dynamic_fields(
        self,
        parent_object_id: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Return the list of dynamic field info for a given object.
        
        Args:
            parent_object_id: The ID of the parent object
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            
        Returns:
            Dictionary containing:
            - data: List of dynamic field info objects
            - hasNextPage: Boolean indicating if more pages exist
            - nextCursor: Cursor for the next page (if hasNextPage is true)
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_object_id(parent_object_id)
        
        params = [parent_object_id]
        if cursor is not None:
            params.append(cursor)
            if limit is not None:
                params.append(limit)
        elif limit is not None:
            params.append(None)  # cursor placeholder
            params.append(limit)
        
        return await self.rest_client.call("suix_getDynamicFields", params)
    
    async def get_dynamic_field_object(
        self,
        parent_object_id: str,
        name: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Return the dynamic field object information for a given name.
        
        Args:
            parent_object_id: The ID of the parent object
            name: The dynamic field name object containing type and value
            
        Returns:
            Dynamic field object data
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_object_id(parent_object_id)
        
        if not isinstance(name, dict):
            raise SuiValidationError("Dynamic field name must be a dictionary")
        
        return await self.rest_client.call("suix_getDynamicFieldObject", [parent_object_id, name])
    
    async def get_owned_objects(
        self,
        owner: str,
        query: Optional[Dict[str, Any]] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Return the list of objects owned by an address.
        
        Args:
            owner: The owner's Sui address
            query: Optional query filter for objects
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            
        Returns:
            Dictionary containing:
            - data: List of owned objects
            - hasNextPage: Boolean indicating if more pages exist
            - nextCursor: Cursor for the next page (if hasNextPage is true)
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_address(owner)
        
        params = [owner]
        if query is not None:
            params.append(query)
        else:
            params.append(None)
            
        if cursor is not None:
            params.append(cursor)
            if limit is not None:
                params.append(limit)
        elif limit is not None:
            params.append(None)  # cursor placeholder
            params.append(limit)
        
        return await self.rest_client.call("suix_getOwnedObjects", params)
    
    async def query_events(
        self,
        query: Dict[str, Any],
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        descending_order: bool = False
    ) -> Dict[str, Any]:
        """
        Return list of events for a specified query criteria.
        
        Args:
            query: Event query filter
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            descending_order: Whether to return results in descending order
            
        Returns:
            Dictionary containing:
            - data: List of events
            - hasNextPage: Boolean indicating if more pages exist
            - nextCursor: Cursor for the next page (if hasNextPage is true)
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        if not isinstance(query, dict):
            raise SuiValidationError("Query must be a dictionary")
        
        params = [query]
        if cursor is not None:
            params.append(cursor)
        else:
            params.append(None)
            
        if limit is not None:
            params.append(limit)
        else:
            params.append(None)
            
        params.append(descending_order)
        
        return await self.rest_client.call("suix_queryEvents", params)
    
    async def query_transaction_blocks(
        self,
        query: Dict[str, Any],
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        descending_order: bool = False
    ) -> Dict[str, Any]:
        """
        Return list of transaction blocks for a specified query criteria.
        
        Args:
            query: Transaction query filter
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            descending_order: Whether to return results in descending order
            
        Returns:
            Dictionary containing:
            - data: List of transaction blocks
            - hasNextPage: Boolean indicating if more pages exist
            - nextCursor: Cursor for the next page (if hasNextPage is true)
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        if not isinstance(query, dict):
            raise SuiValidationError("Query must be a dictionary")
        
        params = [query]
        if cursor is not None:
            params.append(cursor)
        else:
            params.append(None)
            
        if limit is not None:
            params.append(limit)
        else:
            params.append(None)
            
        params.append(descending_order)
        
        return await self.rest_client.call("suix_queryTransactionBlocks", params)
    
    async def resolve_name_service_address(self, name: str) -> Optional[str]:
        """
        Return the resolved address given resolver and name.
        
        Args:
            name: The name to resolve
            
        Returns:
            The resolved address string, or None if not found
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        if not isinstance(name, str) or not name.strip():
            raise SuiValidationError("Name must be a non-empty string")
        
        return await self.rest_client.call("suix_resolveNameServiceAddress", [name])
    
    async def resolve_name_service_names(
        self,
        address: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Return the resolved names given address.
        
        Args:
            address: The address to resolve names for
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            
        Returns:
            Dictionary containing:
            - data: List of resolved names
            - hasNextPage: Boolean indicating if more pages exist
            - nextCursor: Cursor for the next page (if hasNextPage is true)
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        self._validate_address(address)
        
        params = [address]
        if cursor is not None:
            params.append(cursor)
            if limit is not None:
                params.append(limit)
        elif limit is not None:
            params.append(None)  # cursor placeholder
            params.append(limit)
        
        return await self.rest_client.call("suix_resolveNameServiceNames", params)
    
    # Note: Subscription methods (suix_subscribeEvents, suix_subscribeTransaction)
    # require WebSocket support and are not implemented in this REST client.
    # They would need a separate WebSocket client implementation.
    
    def _subscription_not_supported(self, method_name: str) -> None:
        """
        Helper method to indicate subscription methods are not supported.
        
        Args:
            method_name: The name of the subscription method
            
        Raises:
            SuiValidationError: Always, indicating subscriptions are not supported
        """
        raise SuiValidationError(
            f"{method_name} requires WebSocket support and is not available "
            "in the REST client. Use a WebSocket client for real-time subscriptions."
        )
    
    async def subscribe_events(self, *args, **kwargs) -> None:
        """
        Subscription method not supported in REST client.
        
        Raises:
            SuiValidationError: Always, indicating subscriptions are not supported
        """
        self._subscription_not_supported("suix_subscribeEvents")
    
    async def subscribe_transaction(self, *args, **kwargs) -> None:
        """
        Subscription method not supported in REST client.
        
        Raises:
            SuiValidationError: Always, indicating subscriptions are not supported
        """
        self._subscription_not_supported("suix_subscribeTransaction") 