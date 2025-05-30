"""
Utility types and functions for transaction building.
"""

from dataclasses import dataclass
from typing import Any, Optional, Union, List
from typing_extensions import Self

from ..bcs import BcsSerializable, Serializer, Deserializer, U8, U16, U32, U64, U128, U256, Bool, Bytes
from ..types import SuiAddress, ObjectID


@dataclass(frozen=True)
class BcsString(BcsSerializable):
    """BCS-serializable string wrapper."""
    value: str
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize string with length prefix."""
        utf8_bytes = self.value.encode('utf-8')
        serializer.write_vector_length(len(utf8_bytes))
        serializer.write_bytes(utf8_bytes)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize string from BCS."""
        length = deserializer.read_vector_length()
        utf8_bytes = deserializer.read_bytes(length)
        return cls(utf8_bytes.decode('utf-8'))
    
    def __str__(self) -> str:
        return self.value


def encode_pure_value(value: Any, type_hint: Optional[str] = None) -> bytes:
    """
    Encode a pure value using BCS serialization.
    
    Args:
        value: The value to encode
        type_hint: Optional type hint for integer encoding
        
    Returns:
        BCS-encoded bytes
        
    Raises:
        ValueError: If the value type is not supported
    """
    from ..bcs import serialize
    
    if isinstance(value, bool):
        return serialize(Bool(value))
    elif isinstance(value, int):
        if type_hint == "u8":
            return serialize(U8(value))
        elif type_hint == "u16":
            return serialize(U16(value))
        elif type_hint == "u32":
            return serialize(U32(value))
        elif type_hint == "u64":
            return serialize(U64(value))
        elif type_hint == "u128":
            return serialize(U128(value))
        elif type_hint == "u256":
            return serialize(U256(value))
        else:
            # Default to u64 for integers without type hint
            return serialize(U64(value))
    elif isinstance(value, str):
        # Check if it's an address
        if len(value) >= 3 and value.startswith("0x"):
            try:
                address = SuiAddress(value)
                return serialize(address)
            except:
                # If not a valid address, treat as regular string
                return serialize(BcsString(value))
        else:
            return serialize(BcsString(value))
    elif isinstance(value, bytes):
        return serialize(Bytes(value))
    elif isinstance(value, SuiAddress):
        return serialize(value)
    elif isinstance(value, ObjectID):
        return serialize(value)
    else:
        raise ValueError(f"Cannot encode value of type {type(value).__name__}: {value}")


def parse_move_call_target(target: str) -> tuple[str, str, str]:
    """
    Parse a Move call target string into package, module, and function.
    
    Args:
        target: Target string in format "package::module::function"
        
    Returns:
        Tuple of (package, module, function)
        
    Raises:
        ValueError: If target format is invalid
    """
    parts = target.split("::")
    if len(parts) != 3:
        raise ValueError(f"Invalid Move call target format: {target}. Expected 'package::module::function'")
    
    package, module, function = parts
    
    # Validate package ID format
    if not package.startswith("0x"):
        raise ValueError(f"Package ID must start with '0x': {package}")
    
    # Validate module and function names
    if not module or not function:
        raise ValueError(f"Module and function names cannot be empty: {target}")
    
    return package, module, function


def validate_object_id(object_id: str) -> str:
    """
    Validate and normalize an object ID.
    
    Args:
        object_id: Object ID string to validate
        
    Returns:
        Normalized object ID
        
    Raises:
        ValueError: If object ID format is invalid
    """
    if not isinstance(object_id, str):
        raise ValueError(f"Object ID must be a string, got {type(object_id)}")
    
    if not object_id.startswith("0x"):
        raise ValueError(f"Object ID must start with '0x': {object_id}")
    
    # Remove 0x prefix for length check
    hex_part = object_id[2:]
    
    if not hex_part:
        raise ValueError("Object ID cannot be empty after '0x'")
    
    # Check if it's valid hex
    try:
        int(hex_part, 16)
    except ValueError:
        raise ValueError(f"Object ID contains invalid hexadecimal characters: {object_id}")
    
    # Normalize to 64 characters (32 bytes)
    if len(hex_part) < 64:
        hex_part = hex_part.zfill(64)
    elif len(hex_part) > 64:
        raise ValueError(f"Object ID too long: {object_id}")
    
    return f"0x{hex_part}" 