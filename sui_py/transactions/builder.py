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
    AnyArgument, PureArgument, ObjectArgument, ResultArgument, 
    GasCoinArgument, InputArgument, pure, object_arg, gas_coin
)
from .commands import (
    AnyCommand, MoveCallCommand, TransferObjectsCommand, SplitCoinsCommand,
    MergeCoinsCommand, PublishCommand, UpgradeCommand, MakeMoveVecCommand
)
from .ptb import ProgrammableTransactionBlock
from .utils import encode_pure_value, parse_move_call_target, validate_object_id


@dataclass
class ResultHandle:
    """
    Handle to command results for fluent chaining.
    
    This class provides a convenient way to reference command results
    without manually managing command indices.
    """
    command_index: int
    result_count: int = 1
    
    def __getitem__(self, index: int) -> ResultArgument:
        """Get a specific result by index."""
        if index < 0 or index >= self.result_count:
            raise IndexError(f"Result index {index} out of bounds (0-{self.result_count-1})")
        return ResultArgument(self.command_index, index)
    
    def __iter__(self):
        """Iterate over all results."""
        for i in range(self.result_count):
            yield ResultArgument(self.command_index, i)
    
    def single(self) -> ResultArgument:
        """Get the single result (convenience for commands that return one value)."""
        if self.result_count != 1:
            raise ValueError(f"Command has {self.result_count} results, expected 1")
        return ResultArgument(self.command_index, 0)


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
        self._inputs: List[AnyArgument] = []
        self._commands: List[AnyCommand] = []
        self._input_cache: Dict[Any, int] = {}  # For deduplication
        self._gas_coin_used = False
    
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
        obj_arg = ObjectArgument.from_object_id(object_id, version, digest)
        input_index = self._add_input(obj_arg)
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
        command = MoveCallCommand.from_target(
            target=target,
            arguments=converted_args,
            type_arguments=type_arguments or []
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        # Assume single result for now (could be enhanced with function signature analysis)
        return ResultHandle(command_index, result_count=1)
    
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
        
        command = TransferObjectsCommand(
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
            A ResultHandle for the new coins
            
        Example:
            coin = tx.object("0x123...")
            amounts = [tx.pure(1000), tx.pure(2000)]
            new_coins = tx.split_coins(coin, amounts)
        """
        converted_coin = self._convert_argument(coin)
        converted_amounts = [self._convert_argument(amount) for amount in amounts]
        
        command = SplitCoinsCommand(
            coin=converted_coin,
            amounts=converted_amounts
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        # Split returns as many coins as amounts
        return ResultHandle(command_index, result_count=len(amounts))
    
    def merge_coins(self, destination: Any, sources: List[Any]) -> None:
        """
        Add a merge coins command.
        
        Args:
            destination: The destination coin to merge into
            sources: List of source coins to merge
            
        Example:
            main_coin = tx.object("0x123...")
            other_coins = [tx.object("0xabc..."), tx.object("0xdef...")]
            tx.merge_coins(main_coin, other_coins)
        """
        converted_destination = self._convert_argument(destination)
        converted_sources = [self._convert_argument(source) for source in sources]
        
        command = MergeCoinsCommand(
            destination=converted_destination,
            sources=converted_sources
        )
        self._commands.append(command)
    
    def publish(self, modules: List[bytes], dependencies: Optional[List[str]] = None) -> ResultHandle:
        """
        Add a package publish command.
        
        Args:
            modules: List of compiled module bytecode
            dependencies: List of dependency package IDs
            
        Returns:
            A ResultHandle for the UpgradeCap
            
        Example:
            upgrade_cap = tx.publish(compiled_modules, ["0x1", "0x2"])
            tx.transfer_objects([upgrade_cap.single()], deployer_address)
        """
        command = PublishCommand(
            modules=modules,
            dependencies=dependencies or []
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        # Publish returns an UpgradeCap
        return ResultHandle(command_index, result_count=1)
    
    def upgrade(self, 
                modules: List[bytes],
                dependencies: List[str],
                package: str,
                ticket: Any) -> ResultHandle:
        """
        Add a package upgrade command.
        
        Args:
            modules: List of compiled module bytecode
            dependencies: List of dependency package IDs
            package: Package ID to upgrade
            ticket: Upgrade authorization ticket
            
        Returns:
            A ResultHandle for the UpgradeReceipt
            
        Example:
            receipt = tx.upgrade(new_modules, deps, package_id, ticket)
        """
        converted_ticket = self._convert_argument(ticket)
        
        command = UpgradeCommand(
            modules=modules,
            dependencies=dependencies,
            package=package,
            ticket=converted_ticket
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        # Upgrade returns an UpgradeReceipt
        return ResultHandle(command_index, result_count=1)
    
    def make_move_vec(self, elements: List[Any], type_argument: Optional[str] = None) -> ResultHandle:
        """
        Add a make Move vector command.
        
        Args:
            elements: List of elements for the vector
            type_argument: Optional type argument for the vector
            
        Returns:
            A ResultHandle for the created vector
            
        Example:
            vector = tx.make_move_vec([obj1, obj2], "0x2::coin::Coin<0x2::sui::SUI>")
        """
        converted_elements = [self._convert_argument(element) for element in elements]
        
        command = MakeMoveVecCommand(
            type_argument=type_argument,
            elements=converted_elements
        )
        
        command_index = len(self._commands)
        self._commands.append(command)
        
        # Make vector returns a single vector
        return ResultHandle(command_index, result_count=1)
    
    def build(self) -> ProgrammableTransactionBlock:
        """
        Build the final Programmable Transaction Block.
        
        Returns:
            A complete PTB ready for signing and execution
            
        Raises:
            ValueError: If the transaction is invalid
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
    
    def _convert_argument(self, arg: Any) -> AnyArgument:
        """Convert a value to the appropriate argument type."""
        if isinstance(arg, (PureArgument, ObjectArgument, ResultArgument, GasCoinArgument, InputArgument)):
            return arg
        elif isinstance(arg, str) and arg.startswith("0x"):
            # Treat as address - could be object ID or address
            return self.pure(arg)
        elif isinstance(arg, (int, bool, bytes)):
            return self.pure(arg)
        else:
            # Try to convert as pure value
            return self.pure(arg)
    
    def _add_input(self, arg: AnyArgument) -> int:
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
        
        # Additional validation could be added here
        pass
    
    def summary(self) -> str:
        """Get a human-readable summary of the transaction being built."""
        lines = [
            f"Transaction Builder Summary:",
            f"  Inputs: {len(self._inputs)}",
            f"  Commands: {len(self._commands)}",
            f"  Gas coin used: {self._gas_coin_used}",
        ]
        
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