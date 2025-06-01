"""
Result and nested result argument implementations.
"""

from dataclasses import dataclass
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer
from .types import TransactionArgumentKind


@dataclass(frozen=True)
class ResultArgument(BcsSerializable):
    """
    Reference to the result of a previous command.
    
    This matches the C# Result class which only contains an Index field
    representing the command index whose result we want to reference.
    """
    command_index: int  # Maps to C# Result.Index
    
    def __post_init__(self):
        """Validate result argument index."""
        if self.command_index < 0:
            raise ValueError("Command index must be non-negative")
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize with TransactionArgument enum format."""
        serializer.write_u8(TransactionArgumentKind.Result)
        serializer.write_u16(self.command_index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a result argument."""
        command_index = deserializer.read_u16()
        return cls(command_index)


@dataclass(frozen=True)
class NestedResultArgument(BcsSerializable):
    """
    Reference to a nested result from a previous command.
    
    This matches the C# NestedResult class which contains both Index and ResultIndex,
    used for accessing specific elements from commands that return multiple values.
    """
    command_index: int  # Maps to C# NestedResult.Index
    result_index: int   # Maps to C# NestedResult.ResultIndex
    
    def __post_init__(self):
        """Validate nested result argument indices."""
        if self.command_index < 0:
            raise ValueError("Command index must be non-negative")
        if self.result_index < 0:
            raise ValueError("Result index must be non-negative")
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize with TransactionArgument enum format."""
        serializer.write_u8(TransactionArgumentKind.NestedResult)
        serializer.write_u16(self.command_index)
        serializer.write_u16(self.result_index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a nested result argument."""
        command_index = deserializer.read_u16()
        result_index = deserializer.read_u16()
        return cls(command_index, result_index)


def result(command_index: int) -> ResultArgument:
    """Create a result argument."""
    return ResultArgument(command_index)


def nested_result(command_index: int, result_index: int) -> NestedResultArgument:
    """Create a nested result argument."""
    return NestedResultArgument(command_index, result_index)
