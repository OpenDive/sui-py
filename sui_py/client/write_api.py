"""
Write API client for Sui blockchain.

Implements all Write API RPC methods from the Sui JSON-RPC API.
These methods handle transaction execution, dry runs, and development inspection.
"""

import base64
import json
import os
from typing import Any, Dict, List, Optional, Union

from .rest_client import RestClient
from ..exceptions import SuiValidationError
from ..types import SuiAddress, TransactionDigest
from ..types.extended import SuiTransactionBlockResponse
from ..types.write_api import (
    ExecuteTransactionRequestType,
    TransactionBlockResponseOptions,
    DryRunTransactionBlockResponse,
    DevInspectArgs,
    DevInspectResults
)

# Debug flag - can be controlled via environment variable
DEBUG_WRITE_API_RPC = os.getenv('DEBUG_WRITE_API_RPC', 'false').lower() == 'true'

def debug_rpc_log(message: str, data=None):
    """Print RPC debug information if debug mode is enabled"""
    if DEBUG_WRITE_API_RPC:
        print(f"🔍 RPC DEBUG: {message}")
        if data is not None:
            if isinstance(data, (dict, list)):
                print(f"   Data: {json.dumps(data, indent=2, default=str)}")
            else:
                print(f"   Data: {data}")
        print()


class WriteAPIClient:
    """
    Client for Sui Write API operations.
    
    Provides methods for executing transactions, dry runs, and development inspection.
    All methods return typed objects corresponding to the Sui JSON-RPC API schemas.
    
    Implements the three core Write API RPC methods:
    - sui_executeTransactionBlock
    - sui_dryRunTransactionBlock  
    - sui_devInspectTransactionBlock
    """
    
    def __init__(self, rest_client: RestClient):
        """
        Initialize the Write API client.
        
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
    def _prepare_transaction_block(transaction_block: Union[bytes, str]) -> str:
        """
        Prepare transaction block for RPC call.
        
        Args:
            transaction_block: Transaction data as bytes or base64 string
            
        Returns:
            Base64 encoded transaction data
            
        Raises:
            SuiValidationError: If transaction block format is invalid
        """
        if isinstance(transaction_block, bytes):
            return base64.b64encode(transaction_block).decode('utf-8')
        elif isinstance(transaction_block, str):
            # Assume it's already base64 encoded
            try:
                # Validate by trying to decode
                base64.b64decode(transaction_block)
                return transaction_block
            except Exception as e:
                raise SuiValidationError(f"Invalid base64 transaction block: {e}")
        else:
            raise SuiValidationError("Transaction block must be bytes or base64 string")
    
    @staticmethod
    def _prepare_signatures(signature: Union[str, List[str]]) -> List[str]:
        """
        Prepare signatures for RPC call.
        
        Args:
            signature: Single signature or list of signatures
            
        Returns:
            List of signature strings
            
        Raises:
            SuiValidationError: If signature format is invalid
        """
        if isinstance(signature, str):
            return [signature]
        elif isinstance(signature, list):
            if not signature:
                raise SuiValidationError("Signature list cannot be empty")
            for sig in signature:
                if not isinstance(sig, str):
                    raise SuiValidationError("All signatures must be strings")
            return signature
        else:
            raise SuiValidationError("Signature must be string or list of strings")
    
    async def execute_transaction_block(
        self,
        transaction_block: Union[bytes, str],
        signature: Union[str, List[str]],
        *,
        options: Optional[TransactionBlockResponseOptions] = None,
        request_type: Optional[ExecuteTransactionRequestType] = None
    ) -> SuiTransactionBlockResponse:
        """
        Execute a signed transaction block and wait for results.
        
        Args:
            transaction_block: BCS serialized transaction data as bytes or base64 string
            signature: Transaction signature or list of signatures
            options: Options for specifying the content to be returned
            request_type: Client-side execution behavior (deprecated, use options instead)
            
        Returns:
            Transaction execution response
            
        Raises:
            SuiValidationError: If parameters are invalid
            Exception: If RPC call fails
        """
        import warnings
        
        # Add deprecation warning for request_type
        if request_type is not None:
            warnings.warn(
                "request_type parameter is deprecated and will be removed in a future version. "
                "Use 'options' parameter to control server-side response behavior.",
                DeprecationWarning,
                stacklevel=2
            )
        
        # Prepare parameters - match TypeScript SDK structure
        tx_b64 = self._prepare_transaction_block(transaction_block)
        signatures = self._prepare_signatures(signature)
        
        # Build RPC parameters (only 3 parameters, no request_type sent to RPC)
        params = [
            tx_b64,
            signatures,
            options.to_dict() if options else None
        ]
        
        # Make RPC call
        debug_rpc_log("Calling sui_executeTransactionBlock", {
            "method": "sui_executeTransactionBlock",
            "params": params,
            "tx_b64_length": len(tx_b64),
            "signatures_count": len(signatures),
            "options": options.to_dict() if options else None
        })
        
        response = await self.rest_client.call("sui_executeTransactionBlock", params)
        
        debug_rpc_log("Received sui_executeTransactionBlock response", {
            "response_type": type(response),
            "response_keys": list(response.keys()) if isinstance(response, dict) else "Not a dict",
            "has_digest": "digest" in response if isinstance(response, dict) else False,
            "has_effects": "effects" in response if isinstance(response, dict) else False
        })
        
        result = SuiTransactionBlockResponse.from_dict(response)
        
        # Handle client-side request_type logic (like TypeScript SDK)
        if request_type == ExecuteTransactionRequestType.WAIT_FOR_LOCAL_EXECUTION:
            try:
                await self.wait_for_transaction(result.digest)
            except Exception:
                # Ignore errors while waiting (match TypeScript behavior)
                pass
        
        return result
    
    async def wait_for_transaction(
        self,
        digest: str,
        *,
        timeout: float = 30.0,
        poll_interval: float = 1.0
    ) -> SuiTransactionBlockResponse:
        """
        Wait for transaction confirmation.
        
        Args:
            digest: Transaction digest to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds
            
        Returns:
            Final transaction response
            
        Raises:
            asyncio.TimeoutError: If transaction doesn't confirm in time
        """
        import asyncio
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Check transaction status
                response = await self.rest_client.call(
                    "sui_getTransactionBlock",
                    [digest, {"showEffects": True}]
                )
                
                if response.get('effects'):
                    return SuiTransactionBlockResponse.from_dict(response)
                    
            except Exception:
                # Transaction not found yet, continue waiting
                pass
            
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                raise asyncio.TimeoutError(f"Transaction {digest} not confirmed within {timeout}s")
            
            await asyncio.sleep(poll_interval)
    
    async def dry_run_transaction_block(
        self,
        transaction_block: Union[bytes, str]
    ) -> DryRunTransactionBlockResponse:
        """
        Return transaction execution effects including the gas cost summary,
        while the effects are not committed to the chain.
        
        Args:
            transaction_block: BCS serialized transaction data as base64 string or bytes
            
        Returns:
            DryRunTransactionBlockResponse with execution effects
            
        Raises:
            SuiValidationError: If parameters are invalid
            SuiRPCError: If the RPC call fails
        """
        # Prepare transaction block
        tx_b64 = self._prepare_transaction_block(transaction_block)
        
        # Make RPC call
        debug_rpc_log("Calling sui_dryRunTransactionBlock", {
            "method": "sui_dryRunTransactionBlock",
            "params": [tx_b64],
            "tx_b64_length": len(tx_b64)
        })
        
        response = await self.rest_client.call("sui_dryRunTransactionBlock", [tx_b64])
        
        debug_rpc_log("Received sui_dryRunTransactionBlock response", {
            "response_type": type(response),
            "response_keys": list(response.keys()) if isinstance(response, dict) else "Not a dict",
            "has_effects": "effects" in response if isinstance(response, dict) else False
        })
        
        return DryRunTransactionBlockResponse.from_dict(response)
    
    async def dev_inspect_transaction_block(
        self,
        sender: Union[str, SuiAddress],
        transaction_block: Union[bytes, str],
        *,
        gas_price: Optional[Union[int, str]] = None,
        epoch: Optional[Union[int, str]] = None
    ) -> DevInspectResults:
        """
        Runs the transaction in dev-inspect mode. Which allows for nearly any
        transaction (or Move call) with any arguments. Detailed results are provided,
        including both the transaction effects and any return values.
        
        Args:
            sender: The sender's Sui address
            transaction_block: BCS encoded TransactionKind as base64 !string or bytes
            gas_price: Gas price for calculation (optional)
            epoch: The epoch to perform the call (optional)
            
        Returns:
            DevInspectResults with detailed inspection results
            
        Raises:
            SuiValidationError: If parameters are invalid
            Exception: If RPC call fails
        """
        # Validate and prepare parameters
        sender_str = self._validate_address(sender)
        tx_b64 = self._prepare_transaction_block(transaction_block)
        
        # Build RPC parameters - match official API: [sender, transactionBlock, gasPrice, epoch]
        params = [
            sender_str,
            tx_b64,
            str(gas_price) if gas_price is not None else None,
            str(epoch) if epoch is not None else None
        ]
        
        # Make RPC call
        debug_rpc_log("Calling sui_devInspectTransactionBlock", {
            "method": "sui_devInspectTransactionBlock",
            "params": params,
            "sender": str(sender),
            "tx_b64_length": len(tx_b64),
            "gas_price": gas_price,
            "epoch": epoch
        })
        
        response = await self.rest_client.call("sui_devInspectTransactionBlock", params)
        
        debug_rpc_log("Received sui_devInspectTransactionBlock response", {
            "response_type": type(response),
            "response_keys": list(response.keys()) if isinstance(response, dict) else "Not a dict",
            "has_effects": "effects" in response if isinstance(response, dict) else False,
            "has_error": "error" in response if isinstance(response, dict) else False
        })
        
        return DevInspectResults.from_dict(response)
    
    async def sign_and_execute_transaction(
        self,
        transaction,
        signer,
        *,
        options: Optional[TransactionBlockResponseOptions] = None,
        request_type: Optional[ExecuteTransactionRequestType] = None
    ) -> SuiTransactionBlockResponse:
        """
        Sign and execute a transaction in one call (convenience method).
        
        Args:
            transaction: Transaction object or raw bytes
            signer: Signer instance to sign the transaction
            options: Response options for the execution
            request_type: Client-side execution behavior (deprecated)
            
        Returns:
            Transaction execution response
            
        Raises:
            Exception: If signing or execution fails
        """
        # Handle different transaction types
        if hasattr(transaction, 'build') and callable(getattr(transaction, 'build')):
            # Transaction object with build method
            if hasattr(signer, 'toSuiAddress') and callable(getattr(signer, 'toSuiAddress')):
                transaction.setSenderIfNotSet(signer.toSuiAddress())
            transaction_bytes = await transaction.build()
        elif isinstance(transaction, bytes):
            # Raw transaction bytes
            transaction_bytes = transaction
        else:
            raise ValueError("Transaction must be a Transaction object or bytes")
        
        # Sign the transaction
        if hasattr(signer, 'signTransaction') and callable(getattr(signer, 'signTransaction')):
            signature_result = await signer.signTransaction(transaction_bytes)
            signature = signature_result.get('signature') or signature_result
            bytes_to_execute = signature_result.get('bytes', transaction_bytes)
        else:
            raise ValueError("Signer must have a signTransaction method")
        
        # Execute the signed transaction
        return await self.execute_transaction_block(
            transaction_block=bytes_to_execute,
            signature=signature,
            options=options,
            request_type=request_type
        )

    async def execute_built_transaction(
        self,
        transaction_builder,
        account,
        *,
        options: Optional[TransactionBlockResponseOptions] = None
    ) -> SuiTransactionBlockResponse:
        """
        Build, sign and execute a transaction.
        
        Args:
            transaction_builder: TransactionBuilder instance
            account: Account to sign with
            options: Response options
            
        Returns:
            Transaction execution response
        """
        import base64
        
        # Build transaction
        tx_bytes = await transaction_builder.to_bytes(self.rest_client._client)
        
        # Sign transaction
        signature = account.sign_transaction(tx_bytes)
        
        # Execute transaction
        return await self.execute_transaction_block(
            transaction_block=base64.b64encode(tx_bytes).decode('utf-8'),
            signature=signature,
            options=options
        )
