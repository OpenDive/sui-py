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
from ..types import (
    SuiAddress, ObjectID, TransactionDigest,
    DynamicFieldName, DynamicFieldInfo, 
    SuiObjectData, SuiObjectResponse,
    SuiEvent, SuiTransactionBlockResponse,
    Page
)


class ExtendedAPIClient:
    """
    Client for Sui Extended API operations.
    
    Provides methods for querying objects, events, transactions, and dynamic fields.
    All methods return typed objects corresponding to the Sui JSON-RPC API schemas.
    """
    
    def __init__(self, rest_client: RestClient):
        """
        Initialize the Extended API client.
        
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
    def _validate_object_id(object_id: Union[str, ObjectID]) -> str:
        """
        Validate and normalize a Sui object ID.
        
        Args:
            object_id: The object ID string or ObjectID to validate
            
        Returns:
            The normalized object ID string
            
        Raises:
            SuiValidationError: If the object ID format is invalid
        """
        if isinstance(object_id, ObjectID):
            return str(object_id)
        
        if not isinstance(object_id, str):
            raise SuiValidationError("Object ID must be a string or ObjectID")
        
        # Validate using ObjectID constructor
        validated_object_id = ObjectID.from_str(object_id)
        return str(validated_object_id)
    
    @staticmethod
    def _validate_transaction_digest(digest: Union[str, TransactionDigest]) -> str:
        """
        Validate and normalize a transaction digest.
        
        Args:
            digest: The transaction digest string or TransactionDigest to validate
            
        Returns:
            The normalized digest string
            
        Raises:
            SuiValidationError: If the digest format is invalid
        """
        if isinstance(digest, TransactionDigest):
            return str(digest)
        
        if not isinstance(digest, str):
            raise SuiValidationError("Transaction digest must be a string or TransactionDigest")
        
        # Validate using TransactionDigest constructor
        validated_digest = TransactionDigest.from_str(digest)
        return str(validated_digest)
    
    async def get_dynamic_fields(
        self,
        parent_object_id: Union[str, ObjectID],
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Page[DynamicFieldInfo]:
        """
        Return the list of dynamic field info for a given object.
        
        Args:
            parent_object_id: The ID of the parent object
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            
        Returns:
            Page of DynamicFieldInfo objects
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        parent_id_str = self._validate_object_id(parent_object_id)
        
        params = [parent_id_str]
        if cursor is not None:
            params.append(cursor)
            if limit is not None:
                params.append(limit)
        elif limit is not None:
            params.append(None)  # cursor placeholder
            params.append(limit)
        
        response = await self.rest_client.call("suix_getDynamicFields", params)
        return Page.from_dict(response, DynamicFieldInfo.from_dict)
    
    async def get_dynamic_field_object(
        self,
        parent_object_id: Union[str, ObjectID],
        name: Union[Dict[str, Any], DynamicFieldName]
    ) -> SuiObjectResponse:
        """
        Return the dynamic field object information for a given name.
        
        Args:
            parent_object_id: The ID of the parent object
            name: The dynamic field name object containing type and value
            
        Returns:
            SuiObjectResponse object
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        parent_id_str = self._validate_object_id(parent_object_id)
        
        if isinstance(name, DynamicFieldName):
            name_dict = name.to_dict()
        elif isinstance(name, dict):
            name_dict = name
        else:
            raise SuiValidationError("Dynamic field name must be a dictionary or DynamicFieldName")
        
        response = await self.rest_client.call("suix_getDynamicFieldObject", [parent_id_str, name_dict])
        return SuiObjectResponse.from_dict(response)
    
    async def get_owned_objects(
        self,
        owner: Union[str, SuiAddress],
        query: Optional[Dict[str, Any]] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Page[SuiObjectResponse]:
        """
        Return the list of objects owned by an address.
        
        Args:
            owner: The owner's Sui address
            query: Optional query filter for objects
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            
        Returns:
            Page of SuiObjectResponse objects
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        owner_str = self._validate_address(owner)
        
        params = [owner_str]
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
        
        response = await self.rest_client.call("suix_getOwnedObjects", params)
        return Page.from_dict(response, SuiObjectResponse.from_dict)
    
    async def query_events(
        self,
        query: Dict[str, Any],
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        descending_order: bool = False
    ) -> Page[SuiEvent]:
        """
        Return list of events for a specified query criteria.
        
        Args:
            query: The event query criteria
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            descending_order: Whether to return results in descending order
            
        Returns:
            Page of SuiEvent objects
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        if not isinstance(query, dict):
            raise SuiValidationError("Query must be a dictionary")
        
        params = [query]
        if cursor is not None:
            params.append(cursor)
            if limit is not None:
                params.append(limit)
        elif limit is not None:
            params.append(None)  # cursor placeholder
            params.append(limit)
        
        # Add descending order parameter if specified
        if descending_order:
            # Pad params to ensure descending_order is in the right position
            while len(params) < 3:
                params.append(None)
            params.append(descending_order)
        
        response = await self.rest_client.call("suix_queryEvents", params)
        return Page.from_dict(response, SuiEvent.from_dict)
    
    async def query_transaction_blocks(
        self,
        query: Dict[str, Any],
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        descending_order: bool = False
    ) -> Page[SuiTransactionBlockResponse]:
        """
        Return list of transaction blocks for a specified query criteria.
        
        Args:
            query: The transaction query criteria
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            descending_order: Whether to return results in descending order
            
        Returns:
            Page of SuiTransactionBlockResponse objects
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        if not isinstance(query, dict):
            raise SuiValidationError("Query must be a dictionary")
        
        params = [query]
        if cursor is not None:
            params.append(cursor)
            if limit is not None:
                params.append(limit)
        elif limit is not None:
            params.append(None)  # cursor placeholder
            params.append(limit)
        
        # Add descending order parameter if specified
        if descending_order:
            # Pad params to ensure descending_order is in the right position
            while len(params) < 3:
                params.append(None)
            params.append(descending_order)
        
        response = await self.rest_client.call("suix_queryTransactionBlocks", params)
        return Page.from_dict(response, SuiTransactionBlockResponse.from_dict)
    
    async def resolve_name_service_address(self, name: str) -> Optional[SuiAddress]:
        """
        Return the resolved address given resolver and name.
        
        Args:
            name: The name to resolve
            
        Returns:
            SuiAddress if resolved, None otherwise
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        if not isinstance(name, str):
            raise SuiValidationError("Name must be a string")
        
        response = await self.rest_client.call("suix_resolveNameServiceAddress", [name])
        
        if response is None:
            return None
        
        return SuiAddress.from_str(response)
    
    async def resolve_name_service_names(
        self,
        address: Union[str, SuiAddress],
        cursor: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Page[str]:
        """
        Return the resolved names given address.
        
        Args:
            address: The address to resolve names for
            cursor: Optional paging cursor
            limit: Maximum number of items per page
            
        Returns:
            Page of name strings
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        address_str = self._validate_address(address)
        
        params = [address_str]
        if cursor is not None:
            params.append(cursor)
            if limit is not None:
                params.append(limit)
        elif limit is not None:
            params.append(None)  # cursor placeholder
            params.append(limit)
        
        response = await self.rest_client.call("suix_resolveNameServiceNames", params)
        return Page.from_dict(response)  # No parser needed for strings
    
    def _subscription_not_supported(self, method_name: str) -> None:
        """
        Helper method to indicate subscription methods are not supported in REST client.
        
        Args:
            method_name: The name of the subscription method
            
        Raises:
            SuiValidationError: Always, indicating WebSocket is required
        """
        raise SuiValidationError(
            f"{method_name} requires WebSocket connection. "
            "REST client only supports request-response methods. "
            "Use a WebSocket client for subscription methods."
        )
    
    async def subscribe_events(self, *args, **kwargs) -> None:
        """
        Subscribe to events (requires WebSocket).
        
        This method is not supported in the REST client.
        
        Raises:
            SuiValidationError: Always, indicating WebSocket is required
        """
        self._subscription_not_supported("subscribe_events")
    
    async def subscribe_transaction(self, *args, **kwargs) -> None:
        """
        Subscribe to transactions (requires WebSocket).
        
        This method is not supported in the REST client.
        
        Raises:
            SuiValidationError: Always, indicating WebSocket is required
        """
        self._subscription_not_supported("subscribe_transaction") 