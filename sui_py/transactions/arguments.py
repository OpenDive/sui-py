"""
Transaction argument types for Programmable Transaction Blocks.

This module defines all argument types that can be used in PTB commands,
including pure values, object references, and result references.
All arguments implement the BCS protocol for proper serialization.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union, Optional, Any
from typing_extensions import Self

from ..bcs import BcsSerializable, Serializer, Deserializer
from ..types import ObjectRef, SuiAddress
from .utils import encode_pure_value, validate_object_id


class TransactionArgument(BcsSerializable, ABC):
    """Base class for all transaction arguments."""
    
    @abstractmethod
    def get_argument_tag(self) -> int:
        """Get the BCS enum variant tag for this argument type."""
        pass
    
    @abstractmethod
    def serialize_argument_data(self, serializer: Serializer) -> None:
        """Serialize the argument-specific data."""
        pass
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize with proper BCS enum format."""
        serializer.write_u8(self.get_argument_tag())
        self.serialize_argument_data(serializer)


@dataclass(frozen=True)
class PureArgument(TransactionArgument):
    """
    Pure value argument containing BCS-encoded data.
    
    Pure arguments represent primitive values like integers, booleans, 
    addresses, and other non-object data that can be BCS-encoded.
    """
    bcs_bytes: bytes
    
    def get_argument_tag(self) -> int:
        return 0  # Pure variant
    
    def serialize_argument_data(self, serializer: Serializer) -> None:
        """Serialize the pure value as a byte vector."""
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
        bcs_bytes = encode_pure_value(value, type_hint)
        return cls(bcs_bytes)


@dataclass(frozen=True)
class ObjectArgument(TransactionArgument):
    """
    Object reference argument.
    
    Object arguments represent references to on-chain objects,
    including owned objects, shared objects, and immutable objects.
    """
    object_ref: ObjectRef
    
    def get_argument_tag(self) -> int:
        return 1  # Object variant
    
    def serialize_argument_data(self, serializer: Serializer) -> None:
        """Serialize the object reference."""
        # Match C# ObjectArg.Serialize() method:
        # First write ObjectRefType.ImmOrOwned (0 for ImmOrOwned, 1 for Shared)
        serializer.write_u8(0)  # ObjectRefType.ImmOrOwned
        
        # Then serialize the actual object reference
        self.object_ref.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize an object argument."""
        object_ref = ObjectRef.deserialize(deserializer)
        return cls(object_ref)
    
    @classmethod
    def from_object_id(cls, object_id: str, version: Optional[int] = None, digest: Optional[str] = None) -> "ObjectArgument":
        """
        Create an ObjectArgument from an object ID.
        
        Args:
            object_id: The object ID
            version: Optional version number
            digest: Optional object digest
            
        Returns:
            A new ObjectArgument
        """
        normalized_id = validate_object_id(object_id)
        object_ref = ObjectRef(
            object_id=normalized_id,
            version=version or 0,
            digest=digest or ""
        )
        return cls(object_ref)


@dataclass(frozen=True)
class ResultArgument(TransactionArgument):
    """
    Reference to the result of a previous command.
    
    Result arguments allow chaining commands by referencing the output
    of a previous command in the same transaction block.
    """
    command_index: int
    result_index: int = 0
    
    def __post_init__(self):
        """Validate result argument indices."""
        if self.command_index < 0:
            raise ValueError("Command index must be non-negative")
        if self.result_index < 0:
            raise ValueError("Result index must be non-negative")
    
    def get_argument_tag(self) -> int:
        return 2  # Result variant
    
    def serialize_argument_data(self, serializer: Serializer) -> None:
        """Serialize the command and result indices."""
        serializer.write_u16(self.command_index)
        serializer.write_u16(self.result_index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a result argument."""
        command_index = deserializer.read_u16()
        result_index = deserializer.read_u16()
        return cls(command_index, result_index)


@dataclass(frozen=True)
class NestedResultArgument(TransactionArgument):
    """
    Reference to a nested result from a previous command.
    
    Some commands can return nested results (e.g., vectors of objects).
    This argument type allows referencing elements within those nested results.
    """
    command_index: int
    result_index: int
    nested_index: int
    
    def __post_init__(self):
        """Validate nested result argument indices."""
        if self.command_index < 0:
            raise ValueError("Command index must be non-negative")
        if self.result_index < 0:
            raise ValueError("Result index must be non-negative")
        if self.nested_index < 0:
            raise ValueError("Nested index must be non-negative")
    
    def get_argument_tag(self) -> int:
        return 3  # NestedResult variant
    
    def serialize_argument_data(self, serializer: Serializer) -> None:
        """Serialize the command, result, and nested indices."""
        serializer.write_u16(self.command_index)
        serializer.write_u16(self.result_index)
        serializer.write_u16(self.nested_index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a nested result argument."""
        command_index = deserializer.read_u16()
        result_index = deserializer.read_u16()
        nested_index = deserializer.read_u16()
        return cls(command_index, result_index, nested_index)


@dataclass(frozen=True)
class GasCoinArgument(TransactionArgument):
    """
    Special reference to the gas coin.
    
    This argument type represents the gas coin being used to pay for
    the transaction, which can be used in commands like coin splitting.
    """
    
    def get_argument_tag(self) -> int:
        return 4  # GasCoin variant
    
    def serialize_argument_data(self, serializer: Serializer) -> None:
        """Gas coin has no additional data."""
        pass
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a gas coin argument."""
        return cls()


# Type alias for all argument types
AnyArgument = Union[
    PureArgument,
    ObjectArgument, 
    ResultArgument,
    NestedResultArgument,
    GasCoinArgument
]


def deserialize_argument(deserializer: Deserializer) -> AnyArgument:
    """
    Deserialize any transaction argument based on its tag.
    
    Args:
        deserializer: The BCS deserializer
        
    Returns:
        The deserialized argument
        
    Raises:
        ValueError: If the argument tag is unknown
    """
    tag = deserializer.read_u8()
    
    if tag == 0:
        return PureArgument.deserialize(deserializer)
    elif tag == 1:
        return ObjectArgument.deserialize(deserializer)
    elif tag == 2:
        return ResultArgument.deserialize(deserializer)
    elif tag == 3:
        return NestedResultArgument.deserialize(deserializer)
    elif tag == 4:
        return GasCoinArgument.deserialize(deserializer)
    else:
        raise ValueError(f"Unknown argument tag: {tag}")


# Convenience factory functions
def pure(value: Any, type_hint: Optional[str] = None) -> PureArgument:
    """Create a pure argument from a value."""
    return PureArgument.from_value(value, type_hint)


def object_arg(object_id: str, version: Optional[int] = None, digest: Optional[str] = None) -> ObjectArgument:
    """Create an object argument from an object ID."""
    return ObjectArgument.from_object_id(object_id, version, digest)


def result(command_index: int, result_index: int = 0) -> ResultArgument:
    """Create a result argument."""
    return ResultArgument(command_index, result_index)


def nested_result(command_index: int, result_index: int, nested_index: int) -> NestedResultArgument:
    """Create a nested result argument."""
    return NestedResultArgument(command_index, result_index, nested_index)


def gas_coin() -> GasCoinArgument:
    """Create a gas coin argument."""
    return GasCoinArgument() 