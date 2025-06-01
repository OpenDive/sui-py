"""
Pure value argument implementation.
"""

from dataclasses import dataclass
from typing import Any, Optional
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer


@dataclass(frozen=True)
class PureArgument(BcsSerializable):
    """
    Pure value argument containing BCS-encoded data.
    
    Pure arguments represent primitive values like integers, booleans, 
    addresses, and other non-object data that can be BCS-encoded.
    """
    bcs_bytes: bytes
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize as Pure CallArg (tag 0 + length + bytes)."""
        serializer.write_u8(0)  # Pure variant
        serializer.write_vector_length(len(self.bcs_bytes))
        serializer.write_bytes(self.bcs_bytes)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a pure argument."""
        length = deserializer.read_vector_length()
        bcs_bytes = deserializer.read_bytes(length)
        return cls(bcs_bytes)
    
    @classmethod
    def from_value(cls, value: Any, type_hint: Optional[str] = None) -> "PureArgument":
        """
        Create a PureArgument from a Python value.
        
        Args:
            value: The value to encode
            type_hint: Optional type hint for encoding (e.g., "u8", "u64")
            
        Returns:
            A new PureArgument with the encoded value
        """
        from ..utils import encode_pure_value
        bcs_bytes = encode_pure_value(value, type_hint)
        return cls(bcs_bytes)


def pure(value: Any, type_hint: Optional[str] = None) -> PureArgument:
    """Create a pure argument from a value."""
    return PureArgument.from_value(value, type_hint)
