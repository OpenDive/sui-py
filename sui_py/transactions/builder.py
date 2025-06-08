"""
Transaction builder with fluent API for constructing Programmable Transaction Blocks.

This module provides the main TransactionBuilder class that offers a clean,
Pythonic interface for building complex transactions with automatic argument
management, input deduplication, and result chaining.
"""

from typing import List, Union, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from ..bcs import serialize, Serializer, Serializable
from .arguments import (
    PTBInputArgument, TransactionArgument, PureArgument, ObjectArgument, UnresolvedObjectArgument, ResultArgument,
    NestedResultArgument, GasCoinArgument, InputArgument, pure, object_arg, gas_coin
)
from .commands import (
    AnyCommand, MoveCall, TransferObjects, SplitCoins,
    MergeCoins, Publish, Upgrade, MakeMoveVec
)
from .ptb import ProgrammableTransactionBlock
from .utils import encode_pure_value, parse_move_call_target, validate_object_id


@dataclass
class ResultHandle:
    """
    Handle to command results for fluent chaining.
    
    This class provides a convenient way to reference command results
    without manually managing command indices. Uses permissive access
    to support functions with unknown return counts.
    """
    command_index: int
    
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


class TransactionBuilder(Serializable):
    """
    Fluent builder for constructing Programmable Transaction Blocks.
    
    Provides a clean, Pythonic API for building complex transactions with:
    - Automatic argument conversion and BCS encoding
    - Input deduplication and optimization
    - Result chaining between commands
    - Type-safe command construction
    - Built-in validation
    
    Example:
        tx = TransactionBuilder()
        coin = tx.object("0x123...")
        amounts = tx.pure([1000, 2000], "vector<u64>")
        new_coins = tx.split_coins(coin, amounts)
        tx.transfer_objects([new_coins[0]], tx.pure("0xabc..."))
        ptb = tx.build()
    """
    
    def __init__(self):
        """Initialize a new transaction builder."""
        self._inputs: List[PTBInputArgument] = []  # Only PureArgument and ObjectArgument
        self._commands: List[AnyCommand] = [] # List of Commands to be executed in the PTB
        self._input_cache: Dict[Any, int] = {}  # For deduplication
        self._gas_coin_used = False
        self._unresolved_objects: List[Tuple[int, str]] = []  # (input_index, object_id) for resolution
    
    def pure(self, value: Any, type_hint: Optional[str] = None) -> InputArgument:
        """
        Add a pure value argument with automatic BCS encoding.
        
        Args:
            value: The value to encode (int, bool, str, bytes, SuiAddress, etc.)
            type_hint: Optional type hint for encoding (e.g., "u8", "u64", "vector<u8>")
            
        Returns:
            An InputArgument that references the pure value in the PTB inputs
            
        Example:
            amount = tx.pure(1000, "u64")
            recipient = tx.pure("0x123...", "address")
            data = tx.pure(b"hello", "vector<u8>")
        """
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
        command = MoveCall.from_target(
            target=target,
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
        
        command = TransferObjects(
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
        
        command = SplitCoins(
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
        
        command = MergeCoins(
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
        command = Publish(
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
        
        command = Upgrade(
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
        
        command = MakeMoveVec(
            elements=converted_elements,
            type_argument=type_argument
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        return ResultHandle(command_index)
    
    def build(self) -> ProgrammableTransactionBlock:
        """
        Build the final Programmable Transaction Block.
        
        Returns:
            A complete PTB ready for signing and execution
            
        Raises:
            ValueError: If the transaction is invalid or has unresolved objects
        """
        # Validate before building
        self._validate()
        
        ptb = ProgrammableTransactionBlock(
            inputs=self._inputs.copy(),
            commands=self._commands.copy()
        )
        
        # Additional validation
        ptb.validate()
        
        return ptb

    async def build_async(self, client) -> ProgrammableTransactionBlock:
        """
        Build the final PTB with async object resolution.
        
        Args:
            client: SuiClient instance for resolving object references
            
        Returns:
            A complete PTB ready for signing and execution
            
        Raises:
            ValueError: If the transaction is invalid
        """
        # Resolve all unresolved objects first
        await self._resolve_objects(client)
        
        # Now build normally
        return self.build()

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
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the transaction builder by building and serializing the PTB.
        
        Args:
            serializer: The BCS serializer to write data to
        """
        ptb = self.build()
        ptb.serialize(serializer)
    
    def to_bytes(self) -> bytes:
        """
        Serialize the PTB to BCS bytes.
        
        Returns:
            The BCS-encoded transaction data
        """
        ptb = self.build()
        return serialize(ptb)
    
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
        # Simple deduplication based on content
        # For more sophisticated deduplication, we could use content hashing
        cache_key = (type(arg), str(arg))
        
        if cache_key in self._input_cache:
            # Return index of existing input
            return self._input_cache[cache_key]
        
        # Add new input
        index = len(self._inputs)
        self._inputs.append(arg)
        self._input_cache[cache_key] = index
        return index
    
    def _validate(self) -> None:
        """Validate the transaction before building."""
        if not self._commands:
            raise ValueError("Transaction must have at least one command")
        
        # Check for unresolved objects
        if self._unresolved_objects:
            object_ids = [obj_id for _, obj_id in self._unresolved_objects]
            raise ValueError(
                f"Cannot build transaction with {len(self._unresolved_objects)} unresolved objects: {object_ids}. "
                f"Use build_async() with a client, or provide version/digest for all objects."
            )
        
        # Additional validation could be added here
        pass
    
    def summary(self) -> str:
        """Get a human-readable summary of the transaction being built."""
        lines = [
            f"Transaction Builder Summary:",
            f"  Inputs: {len(self._inputs)}",
            f"  Commands: {len(self._commands)}",
            f"  Gas coin used: {self._gas_coin_used}",
            f"  Unresolved objects: {len(self._unresolved_objects)}",
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