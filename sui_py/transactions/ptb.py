"""
Programmable Transaction Block (PTB) implementation.

This module defines the PTB container that holds all inputs and commands
for a transaction, providing complete BCS serialization support.
"""

from dataclasses import dataclass
from typing import List, Union
from typing_extensions import Self

from ..bcs import BcsSerializable, Serializer, Deserializer, BcsVector, bcs_vector, serialize
from .arguments import AnyArgument, deserialize_argument
from .commands import AnyCommand, deserialize_command


@dataclass
class ProgrammableTransactionBlock(BcsSerializable):
    """
    Complete programmable transaction block.
    
    A PTB consists of:
    1. Inputs: Pure values and object references that can be used in commands
    2. Commands: Sequence of operations to execute atomically
    
    The PTB is the core transaction format for Sui, allowing complex
    multi-step operations to be executed atomically with shared state.
    """
    inputs: List[AnyArgument]
    commands: List[AnyCommand]
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the PTB to BCS format.
        
        The serialization format follows the Move specification:
        - Vector of inputs (CallArg)
        - Vector of commands (Command)
        """
        # Serialize inputs
        inputs_vector = bcs_vector(self.inputs)
        inputs_vector.serialize(serializer)
        
        # Serialize commands
        commands_vector = bcs_vector(self.commands)
        commands_vector.serialize(serializer)
    
    def to_bytes(self) -> bytes:
        """
        Serialize the PTB to BCS bytes.
        
        Returns:
            The BCS-encoded PTB data
        """
        return serialize(self)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """
        Deserialize a PTB from BCS format.
        
        Args:
            deserializer: The BCS deserializer
            
        Returns:
            A new ProgrammableTransactionBlock instance
        """
        # Read inputs
        inputs_vector = BcsVector.deserialize(deserializer, deserialize_argument)
        inputs = inputs_vector.to_list()
        
        # Read commands
        commands_vector = BcsVector.deserialize(deserializer, deserialize_command)
        commands = commands_vector.to_list()
        
        return cls(inputs=inputs, commands=commands)
    
    def is_empty(self) -> bool:
        """Check if the PTB has no commands."""
        return len(self.commands) == 0
    
    def input_count(self) -> int:
        """Get the number of inputs."""
        return len(self.inputs)
    
    def command_count(self) -> int:
        """Get the number of commands."""
        return len(self.commands)
    
    def get_command(self, index: int) -> AnyCommand:
        """
        Get a command by index.
        
        Args:
            index: Command index
            
        Returns:
            The command at the specified index
            
        Raises:
            IndexError: If index is out of bounds
        """
        if index < 0 or index >= len(self.commands):
            raise IndexError(f"Command index {index} out of bounds (0-{len(self.commands)-1})")
        return self.commands[index]
    
    def get_input(self, index: int) -> AnyArgument:
        """
        Get an input by index.
        
        Args:
            index: Input index
            
        Returns:
            The input at the specified index
            
        Raises:
            IndexError: If index is out of bounds
        """
        if index < 0 or index >= len(self.inputs):
            raise IndexError(f"Input index {index} out of bounds (0-{len(self.inputs)-1})")
        return self.inputs[index]
    
    def validate(self) -> None:
        """
        Validate the PTB structure.
        
        Checks:
        - Result arguments reference valid command indices
        - Command dependencies are satisfied
        - No circular dependencies
        
        Raises:
            ValueError: If validation fails
        """
        self._validate_result_references()
        self._validate_dependencies()
    
    def _validate_result_references(self) -> None:
        """Validate that all result arguments reference valid commands."""
        from .arguments import ResultArgument, NestedResultArgument
        
        # Check all arguments in all commands
        for cmd_idx, command in enumerate(self.commands):
            if hasattr(command, 'arguments'):
                for arg in command.arguments:
                    if isinstance(arg, (ResultArgument, NestedResultArgument)):
                        if arg.command_index >= cmd_idx:
                            raise ValueError(
                                f"Command {cmd_idx} references result from command {arg.command_index}, "
                                f"but can only reference previous commands"
                            )
                        if arg.command_index >= len(self.commands):
                            raise ValueError(
                                f"Command {cmd_idx} references non-existent command {arg.command_index}"
                            )
            
            # Check other argument fields that might contain result references
            if hasattr(command, 'recipient') and isinstance(command.recipient, (ResultArgument, NestedResultArgument)):
                if command.recipient.command_index >= cmd_idx:
                    raise ValueError(
                        f"Command {cmd_idx} recipient references result from command {command.recipient.command_index}, "
                        f"but can only reference previous commands"
                    )
            
            if hasattr(command, 'coin') and isinstance(command.coin, (ResultArgument, NestedResultArgument)):
                if command.coin.command_index >= cmd_idx:
                    raise ValueError(
                        f"Command {cmd_idx} coin references result from command {command.coin.command_index}, "
                        f"but can only reference previous commands"
                    )
    
    def _validate_dependencies(self) -> None:
        """Validate command dependencies and detect cycles."""
        # For now, we rely on the result reference validation
        # More sophisticated dependency analysis could be added here
        pass
    
    def summary(self) -> str:
        """
        Get a human-readable summary of the PTB.
        
        Returns:
            A string describing the PTB contents
        """
        lines = [
            f"Programmable Transaction Block:",
            f"  Inputs: {len(self.inputs)}",
            f"  Commands: {len(self.commands)}",
        ]
        
        if self.commands:
            lines.append("  Command Types:")
            command_types = {}
            for command in self.commands:
                cmd_type = type(command).__name__
                command_types[cmd_type] = command_types.get(cmd_type, 0) + 1
            
            for cmd_type, count in command_types.items():
                lines.append(f"    {cmd_type}: {count}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        """String representation."""
        return self.summary()
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"ProgrammableTransactionBlock(inputs={len(self.inputs)}, commands={len(self.commands)})" 