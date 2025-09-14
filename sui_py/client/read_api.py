"""
Read API client for Sui blockchain.

Provides methods for reading blockchain state, objects, transactions, and system information.
"""

from typing import Any, Dict, List, Optional, Union

from .rest_client import RestClient
from ..types.base import SuiAddress, ObjectID, TransactionDigest
from ..types.extended import SuiObjectResponse, SuiTransactionBlockResponse
from ..types.read_api import ObjectDataOptions, Checkpoint, CheckpointPage, ProtocolConfig
from ..types.write_api import TransactionBlockResponseOptions
from ..exceptions import SuiValidationError


class ReadAPIClient:
    """
    Client for Sui Read API methods.
    
    Provides access to blockchain state, objects, transactions, checkpoints, and system information.
    """
    
    def __init__(self, rest_client: RestClient):
        """
        Initialize the Read API client.
        
        Args:
            rest_client: The underlying REST client for making RPC calls
        """
        self.rest_client = rest_client
    
    async def get_object(
        self,
        object_id: Union[str, ObjectID],
        *,
        options: Optional[ObjectDataOptions] = None
    ) -> SuiObjectResponse:
        """
        Get object information for a given object ID.
        
        Args:
            object_id: The ID of the object to fetch
            options: Options for specifying which object data to include
            
        Returns:
            Object response containing object data or error information
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If object_id is invalid
        """
        if isinstance(object_id, str):
            object_id = ObjectID.from_str(object_id)
        
        params = [str(object_id)]
        if options:
            params.append(options.to_dict())
        
        result = await self.rest_client.call("sui_getObject", params)
        return SuiObjectResponse.from_dict(result)
    
    async def multi_get_objects(
        self,
        object_ids: List[Union[str, ObjectID]],
        *,
        options: Optional[ObjectDataOptions] = None
    ) -> List[SuiObjectResponse]:
        """
        Get object information for multiple object IDs.
        
        Args:
            object_ids: List of object IDs to fetch
            options: Options for specifying which object data to include
            
        Returns:
            List of object responses
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If any object_id is invalid
        """
        if not object_ids:
            return []
        
        # Convert all object IDs to strings
        str_object_ids = []
        for obj_id in object_ids:
            if isinstance(obj_id, str):
                str_object_ids.append(obj_id)
            else:
                str_object_ids.append(str(obj_id))
        
        params = [str_object_ids]
        if options:
            params.append(options.to_dict())
        
        result = await self.rest_client.call("sui_multiGetObjects", params)
        return [SuiObjectResponse.from_dict(obj) for obj in result]
    
    async def try_get_past_object(
        self,
        object_id: Union[str, ObjectID],
        version: int,
        *,
        options: Optional[ObjectDataOptions] = None
    ) -> SuiObjectResponse:
        """
        Get past object information for a given object ID and version.
        
        Args:
            object_id: The ID of the object to fetch
            version: The version of the object to fetch
            options: Options for specifying which object data to include
            
        Returns:
            Object response containing past object data or error information
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If object_id is invalid or version is negative
            
        TODO: Add comprehensive testing with objects that have version history
        TODO: Add examples showing how to find objects with multiple versions
        TODO: Test with coin objects that have been split/merged
        TODO: Test with NFTs that have been transferred
        TODO: Test error handling for non-existent versions
        """
        if isinstance(object_id, str):
            object_id = ObjectID.from_str(object_id)
        
        if version < 0:
            raise SuiValidationError("Object version must be non-negative")
        
        params = [str(object_id), version]
        if options:
            params.append(options.to_dict())
        
        result = await self.rest_client.call("sui_tryGetPastObject", params)
        return SuiObjectResponse.from_dict(result)
    
    async def get_transaction_block(
        self,
        digest: Union[str, TransactionDigest],
        *,
        options: Optional[TransactionBlockResponseOptions] = None
    ) -> SuiTransactionBlockResponse:
        """
        Get transaction information for a given transaction digest.
        
        Args:
            digest: The digest of the transaction to fetch
            options: Options for specifying which transaction data to include
            
        Returns:
            Transaction block response
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If digest is invalid
        """
        if isinstance(digest, str):
            digest = TransactionDigest.from_str(digest)
        
        params = [str(digest)]
        if options:
            params.append(options.to_dict())
        
        result = await self.rest_client.call("sui_getTransactionBlock", params)
        return SuiTransactionBlockResponse.from_dict(result)
    
    async def multi_get_transaction_blocks(
        self,
        digests: List[Union[str, TransactionDigest]],
        *,
        options: Optional[TransactionBlockResponseOptions] = None
    ) -> List[SuiTransactionBlockResponse]:
        """
        Get transaction information for multiple transaction digests.
        
        Args:
            digests: List of transaction digests to fetch
            options: Options for specifying which transaction data to include
            
        Returns:
            List of transaction block responses
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If any digest is invalid
        """
        if not digests:
            return []
        
        # Convert all digests to strings
        str_digests = []
        for digest in digests:
            if isinstance(digest, str):
                str_digests.append(digest)
            else:
                str_digests.append(str(digest))
        
        params = [str_digests]
        if options:
            params.append(options.to_dict())
        
        result = await self.rest_client.call("sui_multiGetTransactionBlocks", params)
        return [SuiTransactionBlockResponse.from_dict(tx) for tx in result]
    
    async def get_checkpoint(
        self,
        checkpoint_id: Union[str, int]
    ) -> Checkpoint:
        """
        Get checkpoint information by sequence number or digest.
        
        Args:
            checkpoint_id: Checkpoint sequence number (int) or digest (str)
            
        Returns:
            Checkpoint information
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If checkpoint_id is invalid
        """
        if isinstance(checkpoint_id, int):
            if checkpoint_id < 0:
                raise SuiValidationError("Checkpoint sequence number must be non-negative")
        
        # For string checkpoint IDs (digest), pass as string
        # For int checkpoint IDs (sequence number), convert to string
        if isinstance(checkpoint_id, int):
            params = [str(checkpoint_id)]
        else:
            params = [checkpoint_id]
        result = await self.rest_client.call("sui_getCheckpoint", params)
        return Checkpoint.from_dict(result)
    
    async def get_checkpoints(
        self,
        *,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        descending: bool = False
    ) -> CheckpointPage:
        """
        Get paginated list of checkpoints.
        
        Args:
            cursor: Optional cursor for pagination
            limit: Maximum number of checkpoints to return
            descending: Whether to return results in descending order
            
        Returns:
            Paginated checkpoint data
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If limit is invalid
        """
        if limit is not None and limit <= 0:
            raise SuiValidationError("Limit must be positive")
        
        params = [cursor, limit, descending]
        result = await self.rest_client.call("sui_getCheckpoints", params)
        return CheckpointPage.from_dict(result)
    
    async def get_latest_checkpoint_sequence_number(self) -> int:
        """
        Get the sequence number of the latest checkpoint.
        
        Returns:
            Latest checkpoint sequence number
            
        Raises:
            SuiRPCError: If the RPC call fails
        """
        result = await self.rest_client.call("sui_getLatestCheckpointSequenceNumber")
        return int(result)
    
    async def get_chain_identifier(self) -> str:
        """
        Get the chain identifier for the network.
        
        Returns:
            Chain identifier string
            
        Raises:
            SuiRPCError: If the RPC call fails
        """
        result = await self.rest_client.call("sui_getChainIdentifier")
        return str(result)
    
    async def get_protocol_config(
        self,
        *,
        version: Optional[int] = None
    ) -> ProtocolConfig:
        """
        Get protocol configuration for the network.
        
        Args:
            version: Optional protocol version to fetch (defaults to current)
            
        Returns:
            Protocol configuration
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If version is invalid
        """
        if version is not None and version < 0:
            raise SuiValidationError("Protocol version must be non-negative")
        
        params = [version] if version is not None else []
        result = await self.rest_client.call("sui_getProtocolConfig", params)
        return ProtocolConfig.from_dict(result)
    
    async def get_total_transaction_blocks(self) -> int:
        """
        Get the total number of transaction blocks on the network.
        
        Returns:
            Total number of transaction blocks
            
        Raises:
            SuiRPCError: If the RPC call fails
        """
        result = await self.rest_client.call("sui_getTotalTransactionBlocks")
        return int(result)
    
    async def get_events(
        self,
        transaction_digest: Union[str, TransactionDigest]
    ) -> List[Dict[str, Any]]:
        """
        Get events emitted by a transaction.
        
        Args:
            transaction_digest: The digest of the transaction
            
        Returns:
            List of events emitted by the transaction
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If digest is invalid
        """
        if isinstance(transaction_digest, str):
            transaction_digest = TransactionDigest.from_str(transaction_digest)
        
        params = [str(transaction_digest)]
        result = await self.rest_client.call("sui_getEvents", params)
        return result if result else []
    
    async def try_multi_get_past_objects(
        self,
        past_objects: List[Dict[str, Any]],
        *,
        options: Optional[ObjectDataOptions] = None
    ) -> List[SuiObjectResponse]:
        """
        Get past object information for multiple objects by ID and version.
        
        Args:
            past_objects: List of objects with 'objectId' and 'version' keys
            options: Options for specifying which object data to include
            
        Returns:
            List of object responses containing past object data
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If any past_object specification is invalid
            
        TODO: Implement sui_tryMultiGetPastObjects RPC method
        TODO: Add proper validation for past_objects parameter format
        TODO: Add comprehensive testing with objects that have version history
        TODO: Add examples showing how to construct past_objects parameter
        """
        # TODO: Validate past_objects format
        # Expected format: [{"objectId": "0x...", "version": 123}, ...]
        
        if not past_objects:
            return []
        
        # TODO: Validate each past object specification
        for past_obj in past_objects:
            if not isinstance(past_obj, dict):
                raise SuiValidationError("Each past object must be a dictionary")
            if "objectId" not in past_obj or "version" not in past_obj:
                raise SuiValidationError("Each past object must have 'objectId' and 'version' keys")
            if not isinstance(past_obj["version"], int) or past_obj["version"] < 0:
                raise SuiValidationError("Object version must be a non-negative integer")
        
        params = [past_objects]
        if options:
            params.append(options.to_dict())
        
        # TODO: Implement actual RPC call once method is available
        result = await self.rest_client.call("sui_tryMultiGetPastObjects", params)
        return [SuiObjectResponse.from_dict(obj) for obj in result]
    
    async def verify_zklogin_signature(
        self,
        signature: str,
        intent_scope: str = "TransactionData",
        *,
        author: Optional[str] = None,
        epoch: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Verify a zkLogin signature.
        
        Args:
            signature: The zkLogin signature to verify
            intent_scope: The intent scope (TransactionData or PersonalMessage)
            author: Optional author address for verification
            epoch: Optional epoch for verification
            
        Returns:
            Verification result with success status and any errors
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If parameters are invalid
            
        TODO: Implement sui_verifyZkLoginSignature RPC method
        TODO: Add proper zkLogin signature format validation
        TODO: Add comprehensive testing with valid zkLogin signatures
        TODO: Add examples showing zkLogin signature generation and verification
        TODO: Add support for different OAuth providers (Google, Facebook, etc.)
        TODO: Add integration with zkLogin authentication flow
        """
        # TODO: Validate signature format
        if not signature or not isinstance(signature, str):
            raise SuiValidationError("Signature must be a non-empty string")
        
        # TODO: Validate intent scope
        valid_scopes = ["TransactionData", "PersonalMessage"]
        if intent_scope not in valid_scopes:
            raise SuiValidationError(f"Intent scope must be one of: {valid_scopes}")
        
        # TODO: Build proper parameters based on RPC specification
        params = [signature, intent_scope]
        if author:
            params.append(author)
        if epoch is not None:
            params.append(epoch)
        
        # TODO: Implement actual RPC call once method is available
        result = await self.rest_client.call("sui_verifyZkLoginSignature", params)
        return result if result else {"success": False, "errors": ["Method not implemented"]}
