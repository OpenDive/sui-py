"""
Input reference argument implementation.
"""

from dataclasses import dataclass
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer
from .types import TransactionArgumentKind


@dataclass(frozen=True)
class InputArgument(BcsSerializable):
    """
    Reference to a PTB input by index.
    
    This is used in command arguments to reference inputs in the PTB inputs vector.
    Equivalent to C# TransactionBlockInput but with cleaner Python semantics.
    """
    input_index: int
    
    def __post_init__(self):
        """Validate input argument index."""
        if self.input_index < 0:
            raise ValueError("Input index must be non-negative")
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize with TransactionArgument enum format."""
        serializer.write_u8(TransactionArgumentKind.Input)
        serializer.write_u16(self.input_index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize an input argument."""
        input_index = deserializer.read_u16()
        return cls(input_index)
