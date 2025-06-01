"""
Transaction argument types for Programmable Transaction Blocks.

This module defines all argument types used in Sui transactions:
- PTB Input Arguments: Pure values and object references that go in PTB inputs vector
- Command Arguments: References used within commands (GasCoin, Input, Result, NestedResult)

All arguments implement the BCS protocol for proper serialization.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Union, Optional, Any
from typing_extensions import Self

from ..bcs import BcsSerializable, Serializer, Deserializer
from ..types import ObjectRef, SuiAddress


# =============================================================================
# PTB Input Arguments (what goes in the PTB inputs vector)
# =============================================================================

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
        from .utils import encode_pure_value
        bcs_bytes = encode_pure_value(value, type_hint)
        return cls(bcs_bytes)


@dataclass(frozen=True)
class ObjectArgument(BcsSerializable):
    """
    Object reference argument.
    
    Object arguments represent references to on-chain objects,
    including owned objects, shared objects, and immutable objects.
    """
    object_ref: ObjectRef
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize as Object CallArg (tag 1 + object ref type + object ref)."""
        serializer.write_u8(1)  # Object variant
        # ObjectRefType.ImmOrOwned (0) vs ObjectRefType.Shared (1)
        serializer.write_u8(0)  # ImmOrOwned for now
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
        from .utils import validate_object_id
        normalized_id = validate_object_id(object_id)
        object_ref = ObjectRef(
            object_id=normalized_id,
            version=version or 0,
            digest=digest or ""
        )
        return cls(object_ref)


# Type alias for PTB inputs (what actually goes in PTB inputs vector)
PTBInputArgument = Union[PureArgument, ObjectArgument]


# =============================================================================
# Command Arguments (what commands use to reference things)
# =============================================================================

class TransactionArgumentKind(IntEnum):
    """
    Enum representation of TransactionArgument types.
    
    These values correspond to the BCS enum variant tags used in serialization,
    and match the C# SDK TransactionArgumentKind enum exactly.
    """
    GasCoin = 0
    Input = 1
    Result = 2 
    NestedResult = 3


@dataclass(frozen=True)
class GasCoinArgument(BcsSerializable):
    """
    Special reference to the gas coin.
    
    This argument type represents the gas coin being used to pay for
    the transaction, which can be used in commands like coin splitting.
    """
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize with TransactionArgument enum format."""
        serializer.write_u8(TransactionArgumentKind.GasCoin)
        # Gas coin has no additional data
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a gas coin argument."""
        return cls()


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


# Type alias for command arguments (what goes in command fields)
CommandArgument = Union[GasCoinArgument, InputArgument, ResultArgument, NestedResultArgument]

# Type alias for all argument types
AnyArgument = Union[PTBInputArgument, CommandArgument]


# =============================================================================
# Deserialization Functions
# =============================================================================

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
    
    if tag == TransactionArgumentKind.GasCoin:
        return GasCoinArgument.deserialize(deserializer)
    elif tag == TransactionArgumentKind.Input:
        return InputArgument.deserialize(deserializer)
    elif tag == TransactionArgumentKind.Result:
        return ResultArgument.deserialize(deserializer)
    elif tag == TransactionArgumentKind.NestedResult:
        return NestedResultArgument.deserialize(deserializer)
    else:
        raise ValueError(f"Unknown command argument tag: {tag}")


# =============================================================================
# Factory Functions (for clean API)
# =============================================================================

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


# =============================================================================
# Legacy Compatibility (can be removed later)
# =============================================================================

# For backward compatibility during migration
TransactionArgument = CommandArgument
GasCoinTransactionArgument = GasCoinArgument
InputTransactionArgument = InputArgument  
ResultTransactionArgument = ResultArgument
NestedResultTransactionArgument = NestedResultArgument


def deserialize_transaction_argument(deserializer: Deserializer) -> CommandArgument:
    """Legacy function - use deserialize_command_argument instead."""
    return deserialize_command_argument(deserializer) 