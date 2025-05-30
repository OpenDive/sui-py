"""
Unified signature implementation for all cryptographic schemes.
"""

from dataclasses import dataclass

from ..exceptions import SuiValidationError
from .base import AbstractSignature
from .schemes import SignatureScheme


@dataclass(frozen=True)
class Signature(AbstractSignature):
    """
    Unified signature implementation for all cryptographic schemes.
    
    This class provides signature functionality for Ed25519, Secp256k1, and Secp256r1
    by storing the signature bytes along with the scheme identifier.
    """
    _signature_bytes: bytes
    _scheme: SignatureScheme
    
    def __post_init__(self):
        """Validate the signature on creation."""
        if not isinstance(self._signature_bytes, bytes):
            raise SuiValidationError("Signature must be bytes")
        
        if not isinstance(self._scheme, SignatureScheme):
            raise SuiValidationError("Scheme must be a SignatureScheme")
        
        # Validate signature length based on scheme
        expected_lengths = {
            SignatureScheme.ED25519: 64,    # Ed25519 signatures are always 64 bytes
            SignatureScheme.SECP256K1: 64,  # Compact format (r + s, 32 bytes each)
            SignatureScheme.SECP256R1: 64,  # Compact format (r + s, 32 bytes each)
        }
        
        expected_length = expected_lengths.get(self._scheme)
        if expected_length and len(self._signature_bytes) != expected_length:
            raise SuiValidationError(
                f"{self._scheme.value} signature must be {expected_length} bytes, "
                f"got {len(self._signature_bytes)}"
            )
    
    @classmethod
    def from_bytes(cls, signature_bytes: bytes, scheme: SignatureScheme) -> "Signature":
        """
        Create a signature from raw bytes and scheme.
        
        Args:
            signature_bytes: The signature bytes
            scheme: The cryptographic scheme used
            
        Returns:
            A signature instance
            
        Raises:
            SuiValidationError: If the signature bytes are invalid
        """
        return cls(signature_bytes, scheme)
    
    @classmethod
    def from_hex(cls, hex_string: str, scheme: SignatureScheme) -> "Signature":
        """
        Create a signature from a hex string and scheme.
        
        Args:
            hex_string: The signature as hex (with or without 0x prefix)
            scheme: The cryptographic scheme used
            
        Returns:
            A signature instance
            
        Raises:
            SuiValidationError: If the hex string is invalid
        """
        if not isinstance(hex_string, str):
            raise SuiValidationError("Hex string must be a string")
        
        # Remove 0x prefix if present
        hex_clean = hex_string.lower()
        if hex_clean.startswith("0x"):
            hex_clean = hex_clean[2:]
        
        # Validate hex format based on scheme
        expected_lengths = {
            SignatureScheme.ED25519: 128,    # 64 bytes = 128 hex chars
            SignatureScheme.SECP256K1: 128,  # 64 bytes = 128 hex chars  
            SignatureScheme.SECP256R1: 128,  # 64 bytes = 128 hex chars
        }
        
        expected_length = expected_lengths.get(scheme)
        if expected_length and len(hex_clean) != expected_length:
            raise SuiValidationError(
                f"{scheme.value} signature hex must be {expected_length} characters, "
                f"got {len(hex_clean)}"
            )
        
        try:
            signature_bytes = bytes.fromhex(hex_clean)
            return cls.from_bytes(signature_bytes, scheme)
        except ValueError as e:
            raise SuiValidationError(f"Invalid hex string: {e}")
    
    def to_bytes(self) -> bytes:
        """
        Export the signature as bytes.
        
        Returns:
            The signature bytes
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
            The signature scheme
        """
        return self._scheme
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self._scheme.value}Signature(hex={self.to_hex()[:18]}...)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Signature("
            f"scheme={self._scheme}, "
            f"hex='{self.to_hex()}'"
            f")"
        ) 