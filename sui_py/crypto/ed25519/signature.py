"""
Ed25519 signature implementation.
"""

from dataclasses import dataclass

from ...exceptions import SuiValidationError
from ..base import AbstractSignature
from ..schemes import SignatureScheme


@dataclass(frozen=True)
class Signature(AbstractSignature):
    """
    Ed25519 signature implementation.
    
    This class provides Ed25519 signature functionality including
    serialization and validation operations.
    """
    _signature_bytes: bytes
    
    def __post_init__(self):
        """Validate the signature on creation."""
        if not isinstance(self._signature_bytes, bytes):
            raise SuiValidationError("Signature must be bytes")
        
        if len(self._signature_bytes) != 64:
            raise SuiValidationError(
                f"Ed25519 signature must be 64 bytes, got {len(self._signature_bytes)}"
            )
    
    @classmethod
    def from_bytes(cls, signature_bytes: bytes) -> "Signature":
        """
        Create an Ed25519 signature from raw bytes.
        
        Args:
            signature_bytes: The 64-byte signature
            
        Returns:
            An Ed25519 signature instance
            
        Raises:
            SuiValidationError: If the signature bytes are invalid
        """
        if not isinstance(signature_bytes, bytes):
            raise SuiValidationError("Signature must be bytes")
        
        if len(signature_bytes) != 64:
            raise SuiValidationError(
                f"Ed25519 signature must be 64 bytes, got {len(signature_bytes)}"
            )
        
        return cls(signature_bytes)
    
    @classmethod
    def from_hex(cls, hex_string: str) -> "Signature":
        """
        Create an Ed25519 signature from a hex string.
        
        Args:
            hex_string: The signature as hex (with or without 0x prefix)
            
        Returns:
            An Ed25519 signature instance
            
        Raises:
            SuiValidationError: If the hex string is invalid
        """
        if not isinstance(hex_string, str):
            raise SuiValidationError("Hex string must be a string")
        
        # Remove 0x prefix if present
        hex_clean = hex_string.lower()
        if hex_clean.startswith("0x"):
            hex_clean = hex_clean[2:]
        
        # Validate hex format
        if len(hex_clean) != 128:  # 64 bytes = 128 hex chars
            raise SuiValidationError(
                f"Ed25519 signature hex must be 128 characters, got {len(hex_clean)}"
            )
        
        try:
            signature_bytes = bytes.fromhex(hex_clean)
            return cls.from_bytes(signature_bytes)
        except ValueError as e:
            raise SuiValidationError(f"Invalid hex string: {e}")
    
    def to_bytes(self) -> bytes:
        """
        Export the signature as bytes.
        
        Returns:
            The 64-byte signature
        """
        return self._signature_bytes
    
    def to_hex(self) -> str:
        """
        Export the signature as a hex string.
        
        Returns:
            The signature as hex string with 0x prefix
        """
        return "0x" + self._signature_bytes.hex()
    
    @property
    def scheme(self) -> SignatureScheme:
        """
        Get the signature scheme for this signature.
        
        Returns:
            SignatureScheme.ED25519
        """
        return SignatureScheme.ED25519
    
    def __str__(self) -> str:
        """String representation."""
        return f"Ed25519Signature(hex={self.to_hex()[:18]}...)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Ed25519Signature("
            f"scheme={self.scheme}, "
            f"hex='{self.to_hex()}'"
            f")"
        ) 