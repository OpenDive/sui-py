"""
BCS-specific exception classes.

These exceptions provide detailed context for serialization and deserialization errors,
helping developers debug issues with binary canonical serialization.
"""

from typing import Optional


class BcsError(Exception):
    """
    Base class for all BCS-related errors.
    
    This serves as the parent class for all BCS serialization and deserialization
    errors, allowing catch-all error handling when needed.
    """
    pass


class SerializationError(BcsError):
    """
    Raised when serialization of an object fails.
    
    This typically indicates a programming error in the serialization logic
    or an object in an invalid state.
    """
    
    def __init__(self, message: str, object_type: Optional[str] = None):
        self.object_type = object_type
        if object_type:
            super().__init__(f"Failed to serialize {object_type}: {message}")
        else:
            super().__init__(f"Serialization failed: {message}")


class DeserializationError(BcsError):
    """
    Raised when deserialization from bytes fails.
    
    This can indicate corrupted data, unsupported format versions,
    or attempting to deserialize the wrong type.
    """
    
    def __init__(self, message: str, position: Optional[int] = None, expected_type: Optional[str] = None):
        self.position = position
        self.expected_type = expected_type
        
        context_parts = []
        if expected_type:
            context_parts.append(f"expected {expected_type}")
        if position is not None:
            context_parts.append(f"at position {position}")
        
        context = f" ({', '.join(context_parts)})" if context_parts else ""
        super().__init__(f"Deserialization failed: {message}{context}")


class InsufficientDataError(DeserializationError):
    """
    Raised when the deserializer reaches end of data unexpectedly.
    
    This typically indicates truncated or corrupted input data.
    """
    
    def __init__(self, needed: int, available: int, position: int):
        self.needed = needed
        self.available = available
        super().__init__(
            f"Need {needed} bytes but only {available} available",
            position=position
        )


class InvalidDataError(DeserializationError):
    """
    Raised when data contains invalid values for the expected type.
    
    Examples: boolean with value > 1, invalid enum variant, etc.
    """
    
    def __init__(self, message: str, value: Optional[int] = None, position: Optional[int] = None):
        self.value = value
        value_info = f" (got {value})" if value is not None else ""
        super().__init__(f"Invalid data: {message}{value_info}", position=position)


class TypeMismatchError(DeserializationError):
    """
    Raised when attempting to deserialize data as the wrong type.
    
    This helps catch errors where the binary data doesn't match
    the expected schema.
    """
    
    def __init__(self, expected: str, position: Optional[int] = None):
        super().__init__(f"Type mismatch", position=position, expected_type=expected)


class OverflowError(BcsError):
    """
    Raised when a value exceeds the limits of its target type.
    
    This can occur during both serialization (value too large for type)
    and deserialization (encoded value exceeds type limits).
    """
    
    def __init__(self, value: int, type_name: str, max_value: int):
        self.value = value
        self.type_name = type_name
        self.max_value = max_value
        super().__init__(f"Value {value} exceeds maximum for {type_name} (max: {max_value})") 