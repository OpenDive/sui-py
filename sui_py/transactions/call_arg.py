"""
CallArg definitions for Programmable Transaction Block inputs.

This module implements the CallArg system that matches the C# Unity SDK,
representing the different types of arguments that can be passed to PTB inputs.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Union, List, Any
from typing_extensions import Self

from ..bcs import BcsSerializable, Serializer, Deserializer, U16, Bytes


class CallArgKind(IntEnum):
    """
    Enum representation of CallArg types.
    
    These values correspond to the BCS enum variant tags used in serialization.
    """
    Pure = 0
    Object = 1
    Input = 2


@dataclass
class PureCallArg(BcsSerializable):
    """
    Pure value call argument.
    
    Represents a pure value that gets serialized directly into the PTB.
    """
    value: bytes
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the pure value bytes."""
        serializer.write_bytes(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes."""
        value = deserializer.read_bytes(len(deserializer._buffer) - deserializer._position)  # Read remaining
        return cls(value=value)


@dataclass
class ObjectCallArg(BcsSerializable):
    """
    Object reference call argument.
    
    Represents an object reference that can be:
    - ImmOrOwnedObject: An immutable or owned object
    - SharedObject: A shared object with initial_shared_version and mutable flag
    - Receiving: A receiving object
    """
    # For simplicity, we'll store the serialized object reference
    # In practice, this would contain the specific object reference type
    object_ref: bytes
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the object reference."""
        serializer.write_bytes(self.object_ref)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes."""
        object_ref = deserializer.read_bytes(len(deserializer._buffer) - deserializer._position)  # Read remaining
        return cls(object_ref=object_ref)


@dataclass
class InputCallArg(BcsSerializable):
    """
    Input index call argument.
    
    References an input by its index in the PTB inputs array.
    """
    index: int
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the input index as u16."""
        serializer.write_u16(self.index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes."""
        index = deserializer.read_u16()
        return cls(index=index)


# Union type for all CallArg variants
CallArgData = Union[PureCallArg, ObjectCallArg, InputCallArg]


@dataclass
class CallArg(BcsSerializable):
    """
    Wrapper for CallArg variants with proper enum serialization.
    
    This matches the C# SDK CallArg structure where each variant
    is tagged with its enum value during serialization.
    """
    data: CallArgData
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize with enum tag followed by variant data."""
        if isinstance(self.data, PureCallArg):
            serializer.write_u8(CallArgKind.Pure)
            self.data.serialize(serializer)
        elif isinstance(self.data, ObjectCallArg):
            serializer.write_u8(CallArgKind.Object)
            self.data.serialize(serializer)
        elif isinstance(self.data, InputCallArg):
            serializer.write_u8(CallArgKind.Input)
            self.data.serialize(serializer)
        else:
            raise ValueError(f"Unknown CallArg type: {type(self.data)}")
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes."""
        tag = deserializer.read_u8()
        
        if tag == CallArgKind.Pure:
            data = PureCallArg.deserialize(deserializer)
        elif tag == CallArgKind.Object:
            data = ObjectCallArg.deserialize(deserializer)
        elif tag == CallArgKind.Input:
            data = InputCallArg.deserialize(deserializer)
        else:
            raise ValueError(f"Unknown CallArg tag: {tag}")
        
        return cls(data=data)
    
    @classmethod
    def pure(cls, value: bytes) -> "CallArg":
        """Create a Pure CallArg."""
        return cls(data=PureCallArg(value=value))
    
    @classmethod
    def object_ref(cls, object_ref: bytes) -> "CallArg":
        """Create an Object CallArg."""
        return cls(data=ObjectCallArg(object_ref=object_ref))
    
    @classmethod
    def input(cls, index: int) -> "CallArg":
        """Create an Input CallArg."""
        return cls(data=InputCallArg(index=index)) 