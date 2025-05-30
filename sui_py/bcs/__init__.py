"""
Binary Canonical Serialization (BCS) for Sui blockchain.

This module provides a complete implementation of BCS serialization and deserialization
following the Move language specification. It includes:

- Core serializer and deserializer engines
- Protocol interfaces for type-safe serialization
- Generic container types (vectors, options)
- Primitive type wrappers
- Comprehensive error handling

Usage:
    from sui_py.bcs import Serializer, Deserializer, U64, BcsVector
    
    # Serialize data
    serializer = Serializer()
    value = U64(12345)
    value.serialize(serializer)
    data = serializer.to_bytes()
    
    # Deserialize data
    deserializer = Deserializer(data)
    restored_value = U64.deserialize(deserializer)
"""

# Core engine
from .serializer import Serializer
from .deserializer import Deserializer

# Protocol interfaces
from .protocols import (
    Serializable,
    Deserializable, 
    BcsSerializable,
    SizedSerializable,
    VersionedDeserializable
)

# Container types
from .containers import (
    BcsVector,
    BcsOption,
    bcs_vector,
    bcs_option,
    bcs_some,
    bcs_none
)

# Primitive types
from .primitives import (
    U8, U16, U32, U64, U128, U256,
    Bool,
    Bytes,
    FixedBytes,
    u8, u16, u32, u64, u128, u256,
    boolean,
    bytes_value,
    fixed_bytes
)

# Exceptions
from .exceptions import (
    BcsError,
    SerializationError,
    DeserializationError,
    InsufficientDataError,
    InvalidDataError,
    TypeMismatchError,
    OverflowError
)

# Version information
__version__ = "0.1.0"

# Public API
__all__ = [
    # Core engine
    "Serializer",
    "Deserializer",
    
    # Protocols
    "Serializable",
    "Deserializable",
    "BcsSerializable",
    "SizedSerializable", 
    "VersionedDeserializable",
    
    # Container types
    "BcsVector",
    "BcsOption",
    "bcs_vector",
    "bcs_option",
    "bcs_some", 
    "bcs_none",
    
    # Primitive types
    "U8", "U16", "U32", "U64", "U128", "U256",
    "Bool",
    "Bytes",
    "FixedBytes",
    "u8", "u16", "u32", "u64", "u128", "u256",
    "boolean",
    "bytes_value",
    "fixed_bytes",
    
    # Exceptions
    "BcsError",
    "SerializationError", 
    "DeserializationError",
    "InsufficientDataError",
    "InvalidDataError",
    "TypeMismatchError",
    "OverflowError",
]


def serialize(obj: Serializable) -> bytes:
    """
    Convenience function to serialize any BCS-serializable object.
    
    Args:
        obj: Object to serialize (must implement Serializable protocol)
        
    Returns:
        The serialized bytes
        
    Example:
        data = serialize(U64(42))
        vector_data = serialize(bcs_vector([U8(1), U8(2), U8(3)]))
    """
    serializer = Serializer()
    obj.serialize(serializer)
    return serializer.to_bytes()


def deserialize(data: bytes, deserializer_func):
    """
    Convenience function to deserialize BCS data.
    
    Args:
        data: The BCS-encoded bytes to deserialize
        deserializer_func: Function to deserialize the specific type
        
    Returns:
        The deserialized object
        
    Example:
        value = deserialize(data, U64.deserialize)
        vector = deserialize(data, lambda d: BcsVector.deserialize(d, U8.deserialize))
    """
    deserializer = Deserializer(data)
    return deserializer_func(deserializer) 