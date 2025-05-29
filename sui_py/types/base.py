"""
Base types for Sui blockchain data structures.

These types correspond to the fundamental Component Schemas in the Sui JSON-RPC API.
"""

import re
from typing import Any, Dict, Union
from dataclasses import dataclass

from ..exceptions import SuiValidationError


@dataclass(frozen=True)
class SuiAddress:
    """
    A Sui address type with validation.
    
    Sui addresses are 32-byte hex strings with 0x prefix (66 characters total).
    """
    value: str
    
    def __post_init__(self):
        """Validate the address format on creation."""
        if not isinstance(self.value, str):
            raise SuiValidationError("Address must be a string")
        
        if not re.match(r"^0x[a-fA-F0-9]{64}$", self.value):
            raise SuiValidationError(
                f"Invalid Sui address format: {self.value}. "
                "Expected 32-byte hex string with 0x prefix (66 characters total)"
            )
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"SuiAddress('{self.value}')"
    
    @classmethod
    def from_str(cls, address: str) -> "SuiAddress":
        """Create a SuiAddress from a string."""
        return cls(address)


@dataclass(frozen=True)
class ObjectID:
    """
    A Sui object ID type with validation.
    
    Object IDs are 32-byte hex strings with 0x prefix (66 characters total).
    """
    value: str
    
    def __post_init__(self):
        """Validate the object ID format on creation."""
        if not isinstance(self.value, str):
            raise SuiValidationError("Object ID must be a string")
        
        if not re.match(r"^0x[a-fA-F0-9]{64}$", self.value):
            raise SuiValidationError(
                f"Invalid object ID format: {self.value}. "
                "Expected 32-byte hex string with 0x prefix (66 characters total)"
            )
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"ObjectID('{self.value}')"
    
    @classmethod
    def from_str(cls, object_id: str) -> "ObjectID":
        """Create an ObjectID from a string."""
        return cls(object_id)


@dataclass(frozen=True)
class TransactionDigest:
    """
    A transaction digest type with basic validation.
    
    Transaction digests are base58 encoded strings.
    """
    value: str
    
    def __post_init__(self):
        """Validate the transaction digest format on creation."""
        if not isinstance(self.value, str):
            raise SuiValidationError("Transaction digest must be a string")
        
        # Basic length check for base58 encoded strings
        if len(self.value) < 40 or len(self.value) > 50:
            raise SuiValidationError(
                f"Invalid transaction digest format: {self.value}. "
                "Expected base58 encoded string"
            )
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"TransactionDigest('{self.value}')"
    
    @classmethod
    def from_str(cls, digest: str) -> "TransactionDigest":
        """Create a TransactionDigest from a string."""
        return cls(digest)


@dataclass(frozen=True)
class Base64:
    """
    A base64 encoded string type.
    """
    value: str
    
    def __post_init__(self):
        """Validate the base64 format on creation."""
        if not isinstance(self.value, str):
            raise SuiValidationError("Base64 value must be a string")
        
        # Basic validation - base64 strings should only contain valid characters
        import base64
        try:
            base64.b64decode(self.value, validate=True)
        except Exception:
            raise SuiValidationError(f"Invalid base64 format: {self.value}")
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"Base64('{self.value}')"
    
    @classmethod
    def from_str(cls, value: str) -> "Base64":
        """Create a Base64 from a string."""
        return cls(value)
    
    def decode(self) -> bytes:
        """Decode the base64 string to bytes."""
        import base64
        return base64.b64decode(self.value)


@dataclass(frozen=True)
class Hex:
    """
    A hexadecimal string type.
    """
    value: str
    
    def __post_init__(self):
        """Validate the hex format on creation."""
        if not isinstance(self.value, str):
            raise SuiValidationError("Hex value must be a string")
        
        # Remove 0x prefix if present for validation
        hex_value = self.value[2:] if self.value.startswith("0x") else self.value
        
        if not re.match(r"^[a-fA-F0-9]*$", hex_value):
            raise SuiValidationError(f"Invalid hex format: {self.value}")
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"Hex('{self.value}')"
    
    @classmethod
    def from_str(cls, value: str) -> "Hex":
        """Create a Hex from a string."""
        return cls(value)
    
    def to_bytes(self) -> bytes:
        """Convert hex string to bytes."""
        hex_value = self.value[2:] if self.value.startswith("0x") else self.value
        return bytes.fromhex(hex_value) 