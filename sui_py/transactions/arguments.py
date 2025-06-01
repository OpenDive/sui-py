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
    
    This matches the C# Result class which only contains an Index field
    representing the command index whose result we want to reference.
    """
    command_index: int  # Maps to C# Result.Index
    
    def __post_init__(self):
        """Validate result argument index."""
        if self.command_index < 0:
            raise ValueError("Command index must be non-negative")
    
    def get_argument_tag(self) -> int:
        return 2  # Result variant
    
    def serialize_argument_data(self, serializer: Serializer) -> None:
        """Serialize only the command index, matching C# Result.Serialize()."""
        serializer.write_u16(self.command_index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a result argument, matching C# Result.Deserialize()."""
        command_index = deserializer.read_u16()
        return cls(command_index)


@dataclass(frozen=True)
class NestedResultArgument(TransactionArgument):
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
    
    def get_argument_tag(self) -> int:
        return 3  # NestedResult variant
    
    def serialize_argument_data(self, serializer: Serializer) -> None:
        """Serialize both indices, matching C# NestedResult.Serialize()."""
        serializer.write_u16(self.command_index)
        serializer.write_u16(self.result_index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a nested result argument, matching C# NestedResult.Deserialize()."""
        command_index = deserializer.read_u16()
        result_index = deserializer.read_u16()
        return cls(command_index, result_index)


@dataclass(frozen=True)
class GasCoinArgument(TransactionArgument):
    """
    Special reference to the gas coin.
    
    This argument type represents the gas coin being used to pay for
    the transaction, which can be used in commands like coin splitting.
    """
    
    def get_argument_tag(self) -> int:
        return 0  # GasCoin variant (matches C# TransactionArgumentKind.GasCoin)
    
    def serialize_argument_data(self, serializer: Serializer) -> None:
        """Gas coin has no additional data."""
        pass
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a gas coin argument."""
        return cls()


@dataclass(frozen=True)
class InputArgument(TransactionArgument):
    """
    Reference to a PTB input by index.
    
    This is used in command arguments to reference inputs in the PTB inputs vector.
    Based on the C# SDK TransactionArgumentKind enum pattern.
    
    Tag values from C# SDK:
    - GasCoin = 0
    - Input = 1  
    - Result = 2
    - NestedResult = 3
    """
    input_index: int
    
    def __post_init__(self):
        """Validate input argument index."""
        if self.input_index < 0:
            raise ValueError("Input index must be non-negative")
    
    def get_argument_tag(self) -> int:
        # Based on C# SDK TransactionArgumentKind.Input
        return 1  # Input variant (matches C# SDK)
    
    def serialize_argument_data(self, serializer: Serializer) -> None:
        """Serialize the input index."""
        serializer.write_u16(self.input_index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize an input argument."""
        input_index = deserializer.read_u16()
        return cls(input_index)


# Type aliases for different contexts
PTBInputArgument = Union[PureArgument, ObjectArgument]  # Only these go in PTB inputs
CommandArgument = Union[GasCoinArgument, InputArgument, ResultArgument, NestedResultArgument]  # These go in commands
AnyArgument = Union[PTBInputArgument, CommandArgument]  # All argument types


def deserialize_ptb_input(deserializer: Deserializer) -> PTBInputArgument:
    """
    Deserialize a PTB input argument (CallArg in C# SDK).
    
    PTB Input tag values:
    - Pure = 0
    - Object = 1
    
    Args:
        deserializer: The BCS deserializer
        
    Returns:
        The deserialized PTB input argument
        
    Raises:
        ValueError: If the argument tag is unknown
    """
    tag = deserializer.read_u8()
    
    if tag == 0:
        return PureArgument.deserialize(deserializer)
    elif tag == 1:
        return ObjectArgument.deserialize(deserializer)
    else:
        raise ValueError(f"Unknown PTB input argument tag: {tag}")


def deserialize_command_argument(deserializer: Deserializer) -> CommandArgument:
    """
    Deserialize a command argument (TransactionArgument in C# SDK).
    
    Command Argument tag values:
    - GasCoin = 0
    - Input = 1
    - Result = 2
    - NestedResult = 3
    
    Args:
        deserializer: The BCS deserializer
        
    Returns:
        The deserialized command argument
        
    Raises:
        ValueError: If the argument tag is unknown
    """
    tag = deserializer.read_u8()
    
    if tag == 0:
        return GasCoinArgument.deserialize(deserializer)
    elif tag == 1:
        return InputArgument.deserialize(deserializer)
    elif tag == 2:
        return ResultArgument.deserialize(deserializer)
    elif tag == 3:
        return NestedResultArgument.deserialize(deserializer)
    else:
        raise ValueError(f"Unknown command argument tag: {tag}")


def deserialize_argument(deserializer: Deserializer) -> AnyArgument:
    """
    Legacy deserialize function - tries to determine context automatically.
    
    DEPRECATED: Use deserialize_ptb_input() or deserialize_command_argument() instead
    for better type safety and clarity.
    
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


def result(command_index: int) -> ResultArgument:
    """Create a result argument."""
    return ResultArgument(command_index)


def nested_result(command_index: int, result_index: int) -> NestedResultArgument:
    """Create a nested result argument."""
    return NestedResultArgument(command_index, result_index)


def gas_coin() -> GasCoinArgument:
    """Create a gas coin argument."""
    return GasCoinArgument() 