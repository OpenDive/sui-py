"""
Wrapper types for Move primitive values with BCS serialization.

This module provides wrapper classes for all Move primitive types, allowing them
to be used in BCS serialization while maintaining type safety and validation.
"""

from dataclasses import dataclass
from typing import Union, Any
from typing_extensions import Self

from .protocols import BcsSerializable
from .serializer import Serializer
from .deserializer import Deserializer
from .exceptions import SerializationError, DeserializationError, OverflowError


@dataclass(frozen=True)
class U8(BcsSerializable):
    """
    8-bit unsigned integer (0 to 255).
    
    Represents Move's u8 type with BCS serialization support.
    """
    value: int
    
    def __post_init__(self):
        """Validate the value range."""
        if not isinstance(self.value, int):
            raise ValueError(f"U8 value must be an integer, got {type(self.value)}")
        if not (0 <= self.value <= 255):
            raise OverflowError(self.value, "u8", 255)
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the u8 value."""
        serializer.write_u8(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a u8 value."""
        value = deserializer.read_u8()
        return cls(value)
    
    def __int__(self) -> int:
        """Convert to Python int."""
        return self.value


@dataclass(frozen=True)
class U16(BcsSerializable):
    """
    16-bit unsigned integer (0 to 65,535).
    
    Represents Move's u16 type with BCS serialization support.
    """
    value: int
    
    def __post_init__(self):
        """Validate the value range."""
        if not isinstance(self.value, int):
            raise ValueError(f"U16 value must be an integer, got {type(self.value)}")
        if not (0 <= self.value <= 65535):
            raise OverflowError(self.value, "u16", 65535)
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the u16 value."""
        serializer.write_u16(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a u16 value."""
        value = deserializer.read_u16()
        return cls(value)
    
    def __int__(self) -> int:
        """Convert to Python int."""
        return self.value


@dataclass(frozen=True)
class U32(BcsSerializable):
    """
    32-bit unsigned integer (0 to 4,294,967,295).
    
    Represents Move's u32 type with BCS serialization support.
    """
    value: int
    
    def __post_init__(self):
        """Validate the value range."""
        if not isinstance(self.value, int):
            raise ValueError(f"U32 value must be an integer, got {type(self.value)}")
        if not (0 <= self.value <= 4294967295):
            raise OverflowError(self.value, "u32", 4294967295)
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the u32 value."""
        serializer.write_u32(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a u32 value."""
        value = deserializer.read_u32()
        return cls(value)
    
    def __int__(self) -> int:
        """Convert to Python int."""
        return self.value


@dataclass(frozen=True)
class U64(BcsSerializable):
    """
    64-bit unsigned integer (0 to 18,446,744,073,709,551,615).
    
    Represents Move's u64 type with BCS serialization support.
    """
    value: int
    
    def __post_init__(self):
        """Validate the value range."""
        if not isinstance(self.value, int):
            raise ValueError(f"U64 value must be an integer, got {type(self.value)}")
        if not (0 <= self.value <= 18446744073709551615):
            raise OverflowError(self.value, "u64", 18446744073709551615)
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the u64 value."""
        serializer.write_u64(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a u64 value."""
        value = deserializer.read_u64()
        return cls(value)
    
    def __int__(self) -> int:
        """Convert to Python int."""
        return self.value


@dataclass(frozen=True)
class U128(BcsSerializable):
    """
    128-bit unsigned integer (0 to 340,282,366,920,938,463,463,374,607,431,768,211,455).
    
    Represents Move's u128 type with BCS serialization support.
    """
    value: int
    
    def __post_init__(self):
        """Validate the value range."""
        if not isinstance(self.value, int):
            raise ValueError(f"U128 value must be an integer, got {type(self.value)}")
        max_u128 = (1 << 128) - 1
        if not (0 <= self.value <= max_u128):
            raise OverflowError(self.value, "u128", max_u128)
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the u128 value."""
        serializer.write_u128(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a u128 value."""
        value = deserializer.read_u128()
        return cls(value)
    
    def __int__(self) -> int:
        """Convert to Python int."""
        return self.value


@dataclass(frozen=True)
class U256(BcsSerializable):
    """
    256-bit unsigned integer.
    
    Represents Move's u256 type with BCS serialization support.
    """
    value: int
    
    def __post_init__(self):
        """Validate the value range."""
        if not isinstance(self.value, int):
            raise ValueError(f"U256 value must be an integer, got {type(self.value)}")
        max_u256 = (1 << 256) - 1
        if not (0 <= self.value <= max_u256):
            raise OverflowError(self.value, "u256", max_u256)
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the u256 value."""
        serializer.write_u256(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a u256 value."""
        value = deserializer.read_u256()
        return cls(value)
    
    def __int__(self) -> int:
        """Convert to Python int."""
        return self.value


@dataclass(frozen=True)
class Bool(BcsSerializable):
    """
    Boolean value (true or false).
    
    Represents Move's bool type with BCS serialization support.
    """
    value: bool
    
    def __post_init__(self):
        """Validate the value type."""
        if not isinstance(self.value, bool):
            raise ValueError(f"Bool value must be a boolean, got {type(self.value)}")
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the boolean value."""
        serializer.write_bool(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a boolean value."""
        value = deserializer.read_bool()
        return cls(value)
    
    def __bool__(self) -> bool:
        """Convert to Python bool."""
        return self.value


@dataclass(frozen=True)
class Bytes(BcsSerializable):
    """
    Raw byte sequence with length prefix.
    
    This represents a vector<u8> in Move, which is commonly used
    for arbitrary binary data.
    """
    value: bytes
    
    def __post_init__(self):
        """Validate the value type."""
        if not isinstance(self.value, (bytes, bytearray)):
            raise ValueError(f"Bytes value must be bytes or bytearray, got {type(self.value)}")
        # Ensure immutable bytes
        object.__setattr__(self, 'value', bytes(self.value))
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the bytes with length prefix."""
        serializer.write_vector_length(len(self.value))
        serializer.write_bytes(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize bytes with length prefix."""
        length = deserializer.read_vector_length()
        value = deserializer.read_bytes(length)
        return cls(value)
    
    def __len__(self) -> int:
        """Get the length of the byte sequence."""
        return len(self.value)
    
    def __bytes__(self) -> bytes:
        """Convert to Python bytes."""
        return self.value


@dataclass(frozen=True)
class FixedBytes(BcsSerializable):
    """
    Fixed-length byte sequence without length prefix.
    
    This is used for types like addresses, hashes, and other
    fixed-size binary data where the length is known from context.
    """
    value: bytes
    expected_length: int
    
    def __post_init__(self):
        """Validate the value type and length."""
        if not isinstance(self.value, (bytes, bytearray)):
            raise ValueError(f"FixedBytes value must be bytes or bytearray, got {type(self.value)}")
        
        # Ensure immutable bytes
        object.__setattr__(self, 'value', bytes(self.value))
        
        if len(self.value) != self.expected_length:
            raise ValueError(
                f"FixedBytes must be exactly {self.expected_length} bytes, "
                f"got {len(self.value)}"
            )
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the bytes without length prefix."""
        serializer.write_bytes(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer, expected_length: int) -> Self:
        """Deserialize fixed-length bytes."""
        value = deserializer.read_bytes(expected_length)
        return cls(value, expected_length)
    
    def __len__(self) -> int:
        """Get the length of the byte sequence."""
        return len(self.value)
    
    def __bytes__(self) -> bytes:
        """Convert to Python bytes."""
        return self.value


# Convenience factory functions
def u8(value: Union[int, U8]) -> U8:
    """Create a U8 from an integer or existing U8."""
    if isinstance(value, U8):
        return value
    return U8(value)


def u16(value: Union[int, U16]) -> U16:
    """Create a U16 from an integer or existing U16."""
    if isinstance(value, U16):
        return value
    return U16(value)


def u32(value: Union[int, U32]) -> U32:
    """Create a U32 from an integer or existing U32."""
    if isinstance(value, U32):
        return value
    return U32(value)


def u64(value: Union[int, U64]) -> U64:
    """Create a U64 from an integer or existing U64."""
    if isinstance(value, U64):
        return value
    return U64(value)


def u128(value: Union[int, U128]) -> U128:
    """Create a U128 from an integer or existing U128."""
    if isinstance(value, U128):
        return value
    return U128(value)


def u256(value: Union[int, U256]) -> U256:
    """Create a U256 from an integer or existing U256."""
    if isinstance(value, U256):
        return value
    return U256(value)


def boolean(value: Union[bool, Bool]) -> Bool:
    """Create a Bool from a boolean or existing Bool."""
    if isinstance(value, Bool):
        return value
    return Bool(value)


def bytes_value(value: Union[bytes, bytearray, Bytes]) -> Bytes:
    """Create a Bytes from bytes/bytearray or existing Bytes."""
    if isinstance(value, Bytes):
        return value
    return Bytes(value)


def fixed_bytes(value: Union[bytes, bytearray, FixedBytes], expected_length: int) -> FixedBytes:
    """Create a FixedBytes from bytes/bytearray or existing FixedBytes."""
    if isinstance(value, FixedBytes):
        if value.expected_length != expected_length:
            raise ValueError(f"Expected length mismatch: {value.expected_length} vs {expected_length}")
        return value
    return FixedBytes(value, expected_length) 