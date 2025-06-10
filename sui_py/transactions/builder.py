"""
Transaction builder with fluent API for constructing Programmable Transaction Blocks.

This module provides the main TransactionBuilder class that offers a clean,
Pythonic interface for building complex transactions with automatic argument
management, input deduplication, and result chaining.
"""

from typing import List, Union, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from ..bcs import serialize, Serializer, Deserializer
from ..types import SuiAddress, ObjectRef
from ..utils.logging import get_logger
from .arguments import (
    PTBInputArgument, TransactionArgument, PureArgument, ObjectArgument, ReceivingArgument, UnresolvedObjectArgument, ResultArgument,
    NestedResultArgument, GasCoinArgument, InputArgument, pure, object_arg, receiving_arg, gas_coin
)
from .commands import (
    AnyCommand, Command
)
from .ptb import ProgrammableTransactionBlock
from .data import (
    TransactionData, TransactionDataV1, TransactionKind, TransactionKindType,
    GasData, TransactionExpiration, TransactionType
)
from .utils import encode_pure_value, parse_move_call_target, validate_object_id

from ..utils.logging import setup_logging, get_logger
import logging

@dataclass
class ResultHandle:
    """
    Handle to command results for fluent chaining.
    
    This class provides a convenient way to reference command results
    without manually managing command indices. Uses permissive access
    to support functions with unknown return counts.
    """
    command_index: int
    
    setup_logging(level=logging.DEBUG, use_emojis=True)
    logger = get_logger("sui_py.transactions.builder.ResultHandle")
    
    def __getitem__(self, index: int) -> Union[ResultArgument, NestedResultArgument]:
        """Get a specific result by index with permissive bounds checking."""
        if index < 0:
            raise IndexError("Negative indices not supported")
        if index > 50:  # Reasonable sanity check
            raise IndexError(f"Result index {index} exceeds reasonable bounds (0-50)")
        
        # For index 0, we could use either ResultArgument or NestedResultArgument
        # Using NestedResultArgument for consistency
        return NestedResultArgument(self.command_index, index)
    
    def __iter__(self):
        """Iterate over reasonable number of potential results."""
        for i in range(10):  # Most functions return <10 results
            yield self[i]
    
    def single(self) -> ResultArgument:
        """Get the single result (convenience for commands that return one value)."""
        return ResultArgument(self.command_index)


class TransactionBuilder:
    """
    Fluent builder for constructing complete Sui transactions.
    
    Provides a clean, Pythonic API for building complex transactions with:
    - Automatic argument conversion and BCS encoding
    - Input deduplication and optimization
    - Result chaining between commands
    - Type-safe command construction
    - Built-in validation
    - Complete transaction metadata handling
    
    Example:
        tx = TransactionBuilder()
        coin = tx.object("0x123...")
        amounts = tx.pure([1000, 2000], "vector<u64>")
        new_coins = tx.split_coins(coin, amounts)
        tx.transfer_objects([new_coins[0]], tx.pure("0xabc..."))
        
        # Set transaction metadata
        tx.set_sender("0xsender...")
        tx.set_gas_budget(1000000)
        tx.set_gas_price(1000)
        tx.set_gas_payment([gas_coin_ref])
        
        transaction_data = await tx.build()
    """
    
    def __init__(self, strict_validation: bool = False):
        """
        Initialize a new transaction builder.
        
        Args:
            strict_validation: If True, enforces strict validation rules that may
                             reject valid but unusual transactions. If False (default),
                             follows the permissive validation approach of the TypeScript SDK.
        """
        self._inputs: List[PTBInputArgument] = []  # Only PureArgument and ObjectArgument
        self._commands: List[AnyCommand] = [] # List of Commands to be executed in the PTB
        self._input_cache: Dict[Any, int] = {}  # For deduplication
        self._gas_coin_used = False
        self._unresolved_objects: List[Tuple[int, str]] = []  # (input_index, object_id) for resolution
        self._strict_validation = strict_validation
        
        # Transaction metadata
        self._sender: Optional[SuiAddress] = None
        self._gas_budget: Optional[int] = None
        self._gas_price: Optional[int] = None
        self._gas_payment: Optional[List[ObjectRef]] = None
        self._gas_owner: Optional[SuiAddress] = None
        self._expiration: Optional[TransactionExpiration] = None
        
        # Set up logger for this builder instance
        self._logger = get_logger("sui_py.transactions.builder")
    
    @classmethod
    def new_strict(cls) -> 'TransactionBuilder':
        """
        Create a new transaction builder with strict validation enabled.
        
        Strict mode enforces additional validation rules that may reject
        valid but unusual transactions (like empty transactions).
        
        Returns:
            A new TransactionBuilder with strict validation enabled
        """
        return cls(strict_validation=True)
    
    @classmethod  
    def new_permissive(cls) -> 'TransactionBuilder':
        """
        Create a new transaction builder with permissive validation (default).
        
        Permissive mode follows the TypeScript SDK approach, allowing empty
        transactions and other edge cases that are valid on-chain.
        
        Returns:
            A new TransactionBuilder with permissive validation
        """
        return cls(strict_validation=False)
    
    @classmethod
    def from_bytes(cls, bytes_data: bytes) -> 'TransactionBuilder':
        """
        Reconstruct a TransactionBuilder from BCS-encoded transaction bytes.
        
        This enables round-trip serialization testing and transaction inspection.
        
        Args:
            bytes_data: BCS-encoded transaction data bytes
            
        Returns:
            A new TransactionBuilder with the reconstructed transaction
            
        Raises:
            ValueError: If the bytes cannot be deserialized
            
        Example:
            # Round-trip test
            tx1 = TransactionBuilder()
            # ... configure transaction ...
            bytes1 = await tx1.to_bytes()
            tx2 = TransactionBuilder.from_bytes(bytes1)
            bytes2 = await tx2.to_bytes()
            assert bytes1 == bytes2
        """
        from ..bcs import Deserializer
        from .data import TransactionData
        
        # Deserialize the transaction data
        deserializer = Deserializer(bytes_data)
        transaction_data = TransactionData.deserialize(deserializer)
        
        # Create a new builder and populate it from the deserialized data
        builder = cls()
        
        # Set transaction metadata
        v1_data = transaction_data.transaction_data_v1
        builder._sender = v1_data.sender
        builder._gas_budget = int(v1_data.gas_data.budget) if v1_data.gas_data.budget else None
        builder._gas_price = int(v1_data.gas_data.price) if v1_data.gas_data.price else None
        builder._gas_payment = v1_data.gas_data.payment
        builder._gas_owner = v1_data.gas_data.owner
        builder._expiration = v1_data.expiration
        
        # Populate PTB data
        ptb = v1_data.transaction_kind.programmable_transaction
        builder._inputs = ptb.inputs.copy()
        builder._commands = ptb.commands.copy()
        
        return builder
    
    def set_sender(self, sender: Union[str, SuiAddress]) -> 'TransactionBuilder':
        """
        Set the sender address for the transaction.
        
        Args:
            sender: The sender address as string or SuiAddress
            
        Returns:
            Self for method chaining
        """
        if isinstance(sender, str):
            self._sender = SuiAddress(sender)
            # Log if address was automatically padded
            if not sender.startswith('0x') or len(sender) < 66:
                self._logger.info(f"Sender address auto-padded: '{sender}' → '{self._sender}'")
        else:
            self._sender = sender
        return self
    
    def set_gas_budget(self, budget: int) -> 'TransactionBuilder':
        """
        Set the gas budget for the transaction.
        
        Args:
            budget: The gas budget in MIST
            
        Returns:
            Self for method chaining
        """
        self._gas_budget = budget
        return self
    
    def set_gas_price(self, price: int) -> 'TransactionBuilder':
        """
        Set the gas price for the transaction.
        
        Args:
            price: The gas price in MIST per gas unit
            
        Returns:
            Self for method chaining
        """
        self._gas_price = price
        return self
    
    def set_gas_payment(self, payment: List[ObjectRef]) -> 'TransactionBuilder':
        """
        Set the gas payment objects for the transaction.
        
        Args:
            payment: List of gas coin object references
            
        Returns:
            Self for method chaining
        """
        self._gas_payment = payment
        return self
    
    def set_gas_owner(self, owner: Union[str, SuiAddress]) -> 'TransactionBuilder':
        """
        Set the gas owner address (for sponsored transactions).
        
        Args:
            owner: The gas owner address as string or SuiAddress
            
        Returns:
            Self for method chaining
        """
        if isinstance(owner, str):
            self._gas_owner = SuiAddress(owner)
        else:
            self._gas_owner = owner
        return self
    
    def set_expiration_epoch(self, epoch: int) -> 'TransactionBuilder':
        """
        Set the transaction to expire at a specific epoch.
        
        Args:
            epoch: The epoch number when the transaction expires
            
        Returns:
            Self for method chaining
        """
        self._expiration = TransactionExpiration(epoch=epoch)
        return self
    
    def set_no_expiration(self) -> 'TransactionBuilder':
        """
        Set the transaction to never expire.
        
        Returns:
            Self for method chaining
        """
        self._expiration = TransactionExpiration(epoch=None)
        return self

    def pure(self, value: Any, type_hint: Optional[str] = None) -> InputArgument:
        """
        Add a pure value argument with automatic BCS encoding.
        
        Args:
            value: The value to encode (int, bool, str, bytes, SuiAddress, etc.)
            type_hint: Optional type hint for encoding (e.g., "u8", "u64", "vector<u8>")
                      Special case: If value is bytes and type_hint is "bcs", 
                      treats the bytes as pre-serialized BCS data (TypeScript compatibility)
            
        Returns:
            An InputArgument that references the pure value in the PTB inputs
            
        Example:
            amount = tx.pure(1000, "u64")
            recipient = tx.pure("0x123...", "address")
            data = tx.pure(b"hello", "vector<u8>")
            
            # For pre-serialized BCS data (TypeScript compatibility):
            bcs_data = serialize(U64(100))
            tx.pure(bcs_data, "bcs")  # Use raw bytes without additional encoding
        """
        # Handle pre-serialized BCS data for TypeScript compatibility
        if isinstance(value, bytes) and type_hint == "bcs":
            pure_arg = PureArgument(bcs_bytes=value)
        else:
            # Create pure argument with automatic encoding
            pure_arg = PureArgument.from_value(value, type_hint)
        
        input_index = self._add_input(pure_arg)
        return InputArgument(input_index)
    
    def object(self, object_id: str, version: Optional[int] = None, digest: Optional[str] = None) -> InputArgument:
        """
        Add an object reference argument.
        
        Args:
            object_id: The object ID (will be normalized)
            version: Optional version number
            digest: Optional object digest
            
        Returns:
            An InputArgument that references the object in the PTB inputs
            
        Example:
            coin = tx.object("0x123...")
            nft = tx.object("0xabc...", version=5)
        """
        if version is not None and digest is not None:
            # Fully resolved object
            obj_arg = ObjectArgument.from_object_ref(object_id, version, digest)
            input_index = self._add_input(obj_arg)
            return InputArgument(input_index)
        else:
            # Unresolved object - will be resolved during build_async
            normalized_id = validate_object_id(object_id)
            obj_arg = UnresolvedObjectArgument(
                object_id=normalized_id,
                version=version,
                digest=digest
            )
            input_index = self._add_input(obj_arg)
            self._unresolved_objects.append((input_index, normalized_id))
            return InputArgument(input_index)
    
    def gas_coin(self) -> GasCoinArgument:
        """
        Reference the gas coin for this transaction.
        
        Returns:
            A GasCoinArgument that references the gas payment coin
            
        Example:
            gas = tx.gas_coin()
            split_result = tx.split_coins(gas, [tx.pure(1000)])
        """
        self._gas_coin_used = True
        return GasCoinArgument()
    
    def move_call(self, 
                  target: str,
                  arguments: Optional[List[Any]] = None,
                  type_arguments: Optional[List[str]] = None) -> ResultHandle:
        """
        Add a Move function call command.
        
        Args:
            target: Target in format "package::module::function"
            arguments: Function arguments (will be auto-converted)
            type_arguments: Generic type parameters
            
        Returns:
            A ResultHandle for chaining results
            
        Example:
            result = tx.move_call(
                "0x2::coin::split",
                arguments=[coin, amount],
                type_arguments=["0x2::sui::SUI"]
            )
            new_coin = result.single()
        """
        # Convert arguments to proper argument types
        converted_args = []
        for arg in (arguments or []):
            converted_args.append(self._convert_argument(arg))
        
        # Create and add command
        # Parse target into package::module::function
        package, module, function = target.split("::")
        
        # Normalize package address (e.g., "0x2" -> "0x000...002")
        normalized_package = str(SuiAddress(package))
        
        command = Command.move_call(
            package=normalized_package,
            module=module,
            function=function,
            arguments=converted_args,
            type_arguments=type_arguments or []
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        # Return permissive result handle without assuming result count
        return ResultHandle(command_index)
    
    def transfer_objects(self, objects: List[Any], recipient: Any) -> None:
        """
        Add a transfer objects command.
        
        Args:
            objects: List of objects to transfer
            recipient: Recipient address
            
        Example:
            coin = tx.object("0x123...")
            tx.transfer_objects([coin], tx.pure("0xabc..."))
        """
        converted_objects = [self._convert_argument(obj) for obj in objects]
        converted_recipient = self._convert_argument(recipient)
        
        command = Command.transfer_objects(
            objects=converted_objects,
            recipient=converted_recipient
        )
        self._commands.append(command)
    
    def split_coins(self, coin: Any, amounts: List[Any]) -> ResultHandle:
        """
        Add a split coins command.
        
        Args:
            coin: The coin to split
            amounts: List of amounts to split into
            
        Returns:
            A ResultHandle for accessing the new coins
            
        Example:
            coin = tx.object("0x123...")
            amounts = tx.pure([1000, 2000], "vector<u64>")
            new_coins = tx.split_coins(coin, amounts)
            first_coin = new_coins[0]
        """
        converted_coin = self._convert_argument(coin)
        converted_amounts = [self._convert_argument(amount) for amount in amounts]
        
        command = Command.split_coins(
            coin=converted_coin,
            amounts=converted_amounts
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        # Return permissive result handle (split coins returns as many results as amounts)
        return ResultHandle(command_index)
    
    def merge_coins(self, destination: Any, sources: List[Any]) -> None:
        """
        Add a merge coins command.
        
        Args:
            destination: The destination coin to merge into
            sources: List of source coins to merge
            
        Example:
            coin1 = tx.object("0x123...")
            coin2 = tx.object("0x456...")
            coin3 = tx.object("0x789...")
            tx.merge_coins(coin1, [coin2, coin3])
        """
        converted_destination = self._convert_argument(destination)
        converted_sources = [self._convert_argument(source) for source in sources]
        
        command = Command.merge_coins(
            destination=converted_destination,
            sources=converted_sources
        )
        self._commands.append(command)
    
    def publish(self, modules: List[bytes], dependencies: Optional[List[str]] = None) -> ResultHandle:
        """
        Add a package publish command.
        
        Args:
            modules: List of compiled Move module bytecode
            dependencies: List of package dependencies
            
        Returns:
            A ResultHandle for the published package
            
        Example:
            with open("module.mv", "rb") as f:
                bytecode = f.read()
            package = tx.publish([bytecode], dependencies=["0x1", "0x2"])
        """
        command = Command.publish(
            modules=modules,
            dependencies=dependencies or []
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        # Return permissive result handle
        return ResultHandle(command_index)
    
    def upgrade(self, 
                modules: List[bytes],
                dependencies: List[str],
                package: str,
                ticket: Any) -> ResultHandle:
        """
        Add a package upgrade command.
        
        Args:
            modules: List of new compiled Move module bytecode
            dependencies: List of package dependencies
            package: The package ID being upgraded
            ticket: The upgrade capability ticket
            
        Returns:
            A ResultHandle for the upgraded package
            
        Example:
            with open("new_module.mv", "rb") as f:
                bytecode = f.read()
            ticket = tx.object("0x123...")  # UpgradeCap
            upgraded = tx.upgrade([bytecode], ["0x1"], "0xabc...", ticket)
        """
        converted_ticket = self._convert_argument(ticket)
        
        command = Command.upgrade(
            modules=modules,
            dependencies=dependencies,
            package=package,
            ticket=converted_ticket
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        # Return permissive result handle
        return ResultHandle(command_index)
    
    def make_move_vec(self, elements: List[Any], type_argument: Optional[str] = None) -> ResultHandle:
        """
        Add a make Move vector command.
        
        Args:
            elements: List of elements to include in vector
            type_argument: Optional type parameter for the vector
            
        Returns:
            A ResultHandle for the created vector
            
        Example:
            coins = [tx.object("0x123..."), tx.object("0x456...")]
            vector = tx.make_move_vec(coins, "0x2::coin::Coin<0x2::sui::SUI>")
        """
        converted_elements = [self._convert_argument(element) for element in elements]
        
        command = Command.make_move_vec(
            type_argument=type_argument,
            elements=converted_elements
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        return ResultHandle(command_index)
    
    def build_ptb_sync(self) -> ProgrammableTransactionBlock:
        """
        Build just the PTB synchronously (offline) when all objects are resolved.
        
        Returns:
            A complete PTB ready for wrapping in transaction data
            
        Raises:
            ValueError: If the transaction has unresolved objects or is invalid
        """
        # Check for unresolved objects
        if self._unresolved_objects:
            object_ids = [obj_id for _, obj_id in self._unresolved_objects]
            raise ValueError(
                f"Cannot build synchronously with {len(self._unresolved_objects)} unresolved objects: {object_ids}. "
                f"Use build(client) for async resolution or provide version/digest for all objects."
            )
        
        # Validate the transaction
        self._validate()
        
        ptb = ProgrammableTransactionBlock(
            inputs=self._inputs.copy(),
            commands=self._commands.copy()
        )
        
        # Additional validation
        ptb.validate(strict=self._strict_validation)
        
        return ptb

    async def build_ptb(self, client=None) -> ProgrammableTransactionBlock:
        """
        Build just the PTB with optional object resolution.
        
        Args:
            client: Optional SuiClient instance for resolving object references.
                   Required only if transaction has unresolved objects.
            
        Returns:
            A complete PTB ready for wrapping in transaction data
            
        Raises:
            ValueError: If the transaction is invalid or client is required but not provided
        """
        # Check if we need to resolve objects
        if self._unresolved_objects:
            if client is None:
                object_ids = [obj_id for _, obj_id in self._unresolved_objects]
                self._logger.error(f"Client required to resolve {len(self._unresolved_objects)} objects: {object_ids}")
                raise ValueError(
                    f"Client required to resolve {len(self._unresolved_objects)} unresolved objects: {object_ids}. "
                    f"Provide a SuiClient to build() or specify version/digest for all objects."
                )
            # Resolve objects using the client
            self._logger.info(f"Resolving {len(self._unresolved_objects)} unresolved objects...")
            await self._resolve_objects(client)
            self._logger.success(f"Successfully resolved {len(self._unresolved_objects)} objects")
        
        # Use sync build logic after resolution
        return self.build_ptb_sync()

    def build_sync(self) -> TransactionData:
        """
        Build the complete transaction synchronously (offline) when all objects are resolved.
        
        Returns:
            A complete TransactionData ready for signing and execution
            
        Raises:
            ValueError: If the transaction has unresolved objects, missing metadata, or is invalid
        """
        # Validate transaction metadata
        self._validate_transaction_metadata()
        
        # Build the PTB
        ptb = self.build_ptb_sync()
        
        self._logger.debug(f"Built PTB with {len(ptb.inputs)} inputs and {len(ptb.commands)} commands")
        
        # Create transaction kind
        transaction_kind = TransactionKind(
            kind_type=TransactionKindType.ProgrammableTransaction,
            programmable_transaction=ptb
        )
        
        # Create gas data
        gas_data = GasData(
            budget=str(self._gas_budget),
            price=str(self._gas_price),
            payment=self._gas_payment,
            owner=self._gas_owner  # Keep as None when not explicitly set to match TypeScript
        )
        
        # Create transaction data V1
        transaction_data_v1 = TransactionDataV1(
            transaction_kind=transaction_kind,
            sender=self._sender,
            gas_data=gas_data,
            expiration=self._expiration or TransactionExpiration()  # Default to no expiration
        )
        
        # Create complete transaction data
        transaction_data = TransactionData(
            transaction_type=TransactionType.V1,
            transaction_data_v1=transaction_data_v1
        )
        
        transaction_bytes = len(transaction_data.to_bytes())
        self._logger.success(f"Transaction built successfully: {transaction_bytes} bytes")
        
        return transaction_data

    async def build(self, client=None) -> TransactionData:
        """
        Build the complete transaction with optional object resolution.
        
        Usage patterns:
        - await tx.build(client): Resolves objects if needed, always works
        - tx.build_sync(): Fast offline build, requires all objects resolved
        
        Args:
            client: Optional SuiClient instance for resolving object references.
                   Required only if transaction has unresolved objects.
            
        Returns:
            A complete TransactionData ready for signing and execution
            
        Raises:
            ValueError: If the transaction is invalid, missing metadata, or client is required but not provided
        """
        # Check if we need to resolve objects
        if self._unresolved_objects:
            if client is None:
                object_ids = [obj_id for _, obj_id in self._unresolved_objects]
                self._logger.error(f"Client required to resolve {len(self._unresolved_objects)} objects: {object_ids}")
                raise ValueError(
                    f"Client required to resolve {len(self._unresolved_objects)} unresolved objects: {object_ids}. "
                    f"Provide a SuiClient to build() or specify version/digest for all objects."
                )
            # Resolve objects using the client
            self._logger.info(f"Resolving {len(self._unresolved_objects)} unresolved objects...")
            await self._resolve_objects(client)
            self._logger.success(f"Successfully resolved {len(self._unresolved_objects)} objects")
        
        # Use sync build logic after resolution
        return self.build_sync()

    async def _resolve_objects(self, client):
        """
        Resolve all unresolved object references using the provided client.
        
        Args:
            client: SuiClient instance for fetching object data
        """
        if not self._unresolved_objects:
            return
        
        # Get all unique object IDs that need resolution
        object_ids = list(set(obj_id for _, obj_id in self._unresolved_objects))
        
        # Fetch object data in batch
        object_responses = await client.extended_api.multi_get_objects(
            object_ids, 
            options={"showOwner": True}  # We need version and digest
        )
        
        # Create lookup map
        objects_by_id = {}
        for response in object_responses:
            if response.data and not response.error:
                obj_data = response.data
                objects_by_id[obj_data.objectId] = obj_data
        
        # Update all unresolved objects
        for input_index, object_id in self._unresolved_objects:
            if object_id not in objects_by_id:
                raise ValueError(f"Could not resolve object {object_id}")
            
            obj_data = objects_by_id[object_id]
            resolved_arg = ObjectArgument.from_object_ref(
                obj_data.objectId,
                int(obj_data.version),
                obj_data.digest
            )
            self._inputs[input_index] = resolved_arg
        
        # Clear the unresolved list
        self._unresolved_objects.clear()
    
    def to_bytes_sync(self) -> bytes:
        """
        Serialize the complete transaction to BCS bytes synchronously (offline).
        
        Returns:
            The BCS-encoded transaction data
            
        Raises:
            ValueError: If the transaction has unresolved objects or missing metadata
        """
        transaction_data = self.build_sync()
        return serialize(transaction_data)

    async def to_bytes(self, client=None) -> bytes:
        """
        Serialize the complete transaction to BCS bytes with optional object resolution.
        
        Args:
            client: Optional SuiClient instance for resolving object references
            
        Returns:
            The BCS-encoded transaction data
        """
        transaction_data = await self.build(client)
        return serialize(transaction_data)
    
    def _convert_argument(self, arg: Any) -> TransactionArgument:
        """Convert a value to the appropriate command argument type."""
        if isinstance(arg, (ResultArgument, NestedResultArgument, GasCoinArgument, InputArgument)):
            return arg  # Already a command argument
        elif isinstance(arg, str) and arg.startswith("0x"):
            # Treat as address - create pure argument and return input reference
            return self.pure(arg)
        elif isinstance(arg, (int, bool, bytes)):
            # Create pure argument and return input reference
            return self.pure(arg)
        else:
            # Try to convert as pure value
            return self.pure(arg)
    
    def _add_input(self, arg: PTBInputArgument) -> int:
        """Add input with deduplication and return the index."""
        # Create a proper cache key for deduplication
        from .arguments import PureArgument, ObjectArgument, ReceivingArgument
        
        if isinstance(arg, PureArgument):
            cache_key = ("pure", arg.bcs_bytes)
        elif isinstance(arg, ObjectArgument):
            cache_key = ("object_ref", arg.object_ref.object_id, arg.object_ref.version, arg.object_ref.digest)
        elif isinstance(arg, ReceivingArgument):
            # Use the same cache key as ObjectArgument for objects with the same ID/version/digest
            # This matches TypeScript SDK behavior where receiving and regular refs of the same object deduplicate
            cache_key = ("object_ref", arg.receiving_ref.object_id, arg.receiving_ref.version, arg.receiving_ref.digest)
        else:
            # Fallback for other types
            cache_key = (type(arg).__name__, str(arg))
        
        if cache_key in self._input_cache:
            # Return index of existing input
            return self._input_cache[cache_key]
        
        # Add new input
        index = len(self._inputs)
        self._inputs.append(arg)
        self._input_cache[cache_key] = index
        return index
    
    def _validate(self) -> None:
        """
        Validate the transaction before building.
        
        In strict mode, enforces stricter validation rules.
        In non-strict mode (default), follows TypeScript SDK's permissive approach.
        """
        if not self._commands:
            if self._strict_validation:
                raise ValueError("Transaction must have at least one command (strict mode)")
            else:
                # In non-strict mode, allow empty transactions like TypeScript SDK
                self._logger.warning(
                    "Building transaction with no commands. This creates an empty transaction "
                    "that only processes gas payment. Use strict_validation=True to disallow this."
                )
        
        # Additional validation could be added here
        pass
    
    def _validate_transaction_metadata(self) -> None:
        """Validate that all required transaction metadata is provided."""
        if self._sender is None:
            raise ValueError("Transaction sender is required. Use set_sender() to specify.")
        
        if self._gas_budget is None:
            raise ValueError("Gas budget is required. Use set_gas_budget() to specify.")
        
        if self._gas_price is None:
            raise ValueError("Gas price is required. Use set_gas_price() to specify.")
        
        if self._gas_payment is None:
            raise ValueError("Gas payment objects are required. Use set_gas_payment() to specify.")
        
        if not self._gas_payment:
            raise ValueError("At least one gas payment object is required.")
    
    def summary(self) -> str:
        """Get a human-readable summary of the transaction being built."""
        lines = [
            f"Transaction Builder Summary:",
            f"  Validation mode: {'Strict' if self._strict_validation else 'Permissive (TypeScript SDK compatible)'}",
            f"  Inputs: {len(self._inputs)}",
            f"  Commands: {len(self._commands)}",
            f"  Gas coin used: {self._gas_coin_used}",
            f"  Unresolved objects: {len(self._unresolved_objects)}",
            f"",
            f"Transaction Metadata:",
            f"  Sender: {self._sender}",
            f"  Gas budget: {self._gas_budget}",
            f"  Gas price: {self._gas_price}",
            f"  Gas payment: {len(self._gas_payment) if self._gas_payment else 0} objects",
            f"  Gas owner: {self._gas_owner}",
            f"  Expiration: {self._expiration}",
        ]
        
        if self._unresolved_objects:
            lines.append("  Unresolved object IDs:")
            for _, obj_id in self._unresolved_objects:
                lines.append(f"    {obj_id}")
        
        if self._commands:
            lines.append("  Command Types:")
            command_types = {}
            for command in self._commands:
                cmd_type = type(command).__name__
                command_types[cmd_type] = command_types.get(cmd_type, 0) + 1
            
            for cmd_type, count in command_types.items():
                lines.append(f"    {cmd_type}: {count}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        """String representation."""
        return self.summary()
    
    def __len__(self) -> int:
        """Return the number of commands."""
        return len(self._commands)

    def to_json(self) -> str:
        """
        Get a JSON representation of the transaction structure for debugging.
        
        Returns a JSON string similar to TypeScript SDK's toJSON() method,
        showing the complete transaction structure before BCS serialization.
        
        Returns:
            JSON string representation of the transaction
            
        Raises:
            ValueError: If transaction has missing metadata or unresolved objects
        """
        import json
        
        # Build the transaction to get complete data
        transaction_data = self.build_sync()
        
        # Convert to dictionary structure matching TypeScript format
        transaction_dict = {
            "version": 2,  # Match TypeScript version
            "sender": str(transaction_data.transaction_data_v1.sender) if transaction_data.transaction_data_v1.sender else None,
            "expiration": self._expiration_to_dict(transaction_data.transaction_data_v1.expiration),
            "gasData": {
                "budget": transaction_data.transaction_data_v1.gas_data.budget,
                "price": transaction_data.transaction_data_v1.gas_data.price,
                "owner": str(transaction_data.transaction_data_v1.gas_data.owner) if transaction_data.transaction_data_v1.gas_data.owner else None,
                "payment": [
                    {
                        "objectId": str(ref.object_id),
                        "version": str(ref.version),
                        "digest": ref.digest
                    }
                    for ref in (transaction_data.transaction_data_v1.gas_data.payment or [])
                ]
            },
            "inputs": [self._input_to_dict(inp) for inp in transaction_data.transaction_data_v1.transaction_kind.programmable_transaction.inputs],
            "commands": [self._command_to_dict(cmd) for cmd in transaction_data.transaction_data_v1.transaction_kind.programmable_transaction.commands]
        }
        
        return json.dumps(transaction_dict, indent=2)
    
    def _expiration_to_dict(self, expiration) -> dict:
        """Convert transaction expiration to dictionary format."""
        if expiration is None or expiration.epoch is None:
            return None
        return {"Epoch": expiration.epoch}
    
    def _input_to_dict(self, input_arg) -> dict:
        """Convert PTB input argument to dictionary format."""
        from .arguments import PureArgument, ObjectArgument, ReceivingArgument
        
        if isinstance(input_arg, PureArgument):
            import base64
            return {
                "Pure": {
                    "bytes": base64.b64encode(input_arg.bcs_bytes).decode('utf-8')
                }
            }
        elif isinstance(input_arg, ObjectArgument):
            return {
                "Object": {
                    "ImmOrOwnedObject": {
                        "objectId": str(input_arg.object_ref.object_id),
                        "version": str(input_arg.object_ref.version),
                        "digest": input_arg.object_ref.digest
                    }
                }
            }
        elif isinstance(input_arg, ReceivingArgument):
            return {
                "Object": {
                    "ReceivingObject": {
                        "objectId": str(input_arg.receiving_ref.object_id),
                        "version": str(input_arg.receiving_ref.version),
                        "digest": input_arg.receiving_ref.digest
                    }
                }
            }
        else:
            return {"Unknown": str(type(input_arg).__name__)}
    
    def _command_to_dict(self, command) -> dict:
        """Convert command to dictionary format."""
        from .commands import SplitCoins, MergeCoins, TransferObjects, MoveCall, Publish, Upgrade, MakeMoveVec
        
        if isinstance(command, SplitCoins):
            return {
                "SplitCoins": {
                    "coin": self._argument_to_dict(command.coin),
                    "amounts": [self._argument_to_dict(amt) for amt in command.amounts]
                }
            }
        elif isinstance(command, MergeCoins):
            return {
                "MergeCoins": {
                    "destination": self._argument_to_dict(command.destination),
                    "sources": [self._argument_to_dict(src) for src in command.sources]
                }
            }
        elif isinstance(command, TransferObjects):
            return {
                "TransferObjects": {
                    "objects": [self._argument_to_dict(obj) for obj in command.objects],
                    "address": self._argument_to_dict(command.recipient)
                }
            }
        elif isinstance(command, MoveCall):
            return {
                "MoveCall": {
                    "package": str(command.package),
                    "module": command.module,
                    "function": command.function,
                    "typeArguments": command.type_arguments,
                    "arguments": [self._argument_to_dict(arg) for arg in command.arguments]
                }
            }
        elif isinstance(command, Publish):
            return {
                "Publish": {
                    "modules": [[b for b in module] for module in command.modules],
                    "dependencies": [str(dep) for dep in command.dependencies]
                }
            }
        elif isinstance(command, Upgrade):
            return {
                "Upgrade": {
                    "modules": [[b for b in module] for module in command.modules],
                    "dependencies": [str(dep) for dep in command.dependencies],
                    "package": str(command.package),
                    "ticket": self._argument_to_dict(command.ticket)
                }
            }
        elif isinstance(command, MakeMoveVec):
            return {
                "MakeMoveVec": {
                    "type": command.type_argument,
                    "elements": [self._argument_to_dict(elem) for elem in command.elements]
                }
            }
        else:
            return {"Unknown": str(type(command).__name__)}
    
    def _argument_to_dict(self, argument) -> dict:
        """Convert transaction argument to dictionary format."""
        from .arguments import GasCoinArgument, InputArgument, ResultArgument, NestedResultArgument
        
        if isinstance(argument, GasCoinArgument):
            return {"GasCoin": True}
        elif isinstance(argument, InputArgument):
            return {"Input": argument.input_index}
        elif isinstance(argument, ResultArgument):
            return {"Result": argument.command_index}
        elif isinstance(argument, NestedResultArgument):
            return {"NestedResult": [argument.command_index, argument.result_index]}
        else:
            return {"Unknown": str(type(argument).__name__)}

    async def to_json_async(self, client=None) -> str:
        """
        Async version of to_json that can resolve unresolved objects.
        
        Args:
            client: Optional SuiClient for resolving objects
            
        Returns:
            JSON string representation of the transaction
        """
        import json
        
        # Build the transaction (with optional object resolution)
        transaction_data = await self.build(client)
        
        # Use the same conversion logic as sync version
        # (Implementation would be same as to_json but using async build)
        # For brevity, implementing via build_sync after resolution
        return self.to_json()

    def receiving_ref(self, object_id: str, version: int, digest: str) -> InputArgument:
        """
        Add a receiving object reference argument.
        
        Receiving arguments represent objects being transferred TO this transaction,
        as opposed to objects already owned by the sender.
        
        Args:
            object_id: The receiving object ID
            version: The object version number
            digest: The object digest
            
        Returns:
            An InputArgument that references the receiving object in the PTB inputs
            
        Example:
            receiving_obj = tx.receiving_ref("0x123...", version=5, digest="abc...")
            tx.move_call("0x2::module::receive_object", arguments=[receiving_obj])
        """
        receiving_arg_obj = ReceivingArgument.from_receiving_ref(object_id, version, digest)
        input_index = self._add_input(receiving_arg_obj)
        return InputArgument(input_index) 