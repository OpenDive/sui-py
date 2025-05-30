"""
Ed25519 public key implementation using PyNaCl.
"""

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import nacl.signing
import nacl.encoding

from ...exceptions import SuiValidationError
from ...types.base import SuiAddress
from ..base import AbstractPublicKey
from ..schemes import SignatureScheme

if TYPE_CHECKING:
    from .signature import Signature


@dataclass(frozen=True)
class PublicKey(AbstractPublicKey):
    """
    Ed25519 public key implementation.
    
    This class provides Ed25519 public key functionality including
    signature verification and Sui address derivation.
    """
    _key: nacl.signing.VerifyKey
    
    def __post_init__(self):
        """Validate the public key on creation."""
        if not isinstance(self._key, nacl.signing.VerifyKey):
            raise SuiValidationError("Invalid Ed25519 public key")
    
    @classmethod
    def from_bytes(cls, key_bytes: bytes) -> "PublicKey":
        """
        Create an Ed25519 public key from raw bytes.
        
        Args:
            key_bytes: The 32-byte public key
            
        Returns:
            An Ed25519 public key instance
            
        Raises:
            SuiValidationError: If the key bytes are invalid
        """
        if not isinstance(key_bytes, bytes):
            raise SuiValidationError("Public key must be bytes")
        
        if len(key_bytes) != 32:
            raise SuiValidationError(
                f"Ed25519 public key must be 32 bytes, got {len(key_bytes)}"
            )
        
        try:
            verify_key = nacl.signing.VerifyKey(key_bytes)
            return cls(verify_key)
        except Exception as e:
            raise SuiValidationError(f"Invalid Ed25519 public key bytes: {e}")
    
    @classmethod
    def from_hex(cls, hex_string: str) -> "PublicKey":
        """
        Create an Ed25519 public key from a hex string.
        
        Args:
            hex_string: The public key as hex (with or without 0x prefix)
            
        Returns:
            An Ed25519 public key instance
            
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
        if len(hex_clean) != 64:  # 32 bytes = 64 hex chars
            raise SuiValidationError(
                f"Ed25519 public key hex must be 64 characters, got {len(hex_clean)}"
            )
        
        try:
            key_bytes = bytes.fromhex(hex_clean)
            return cls.from_bytes(key_bytes)
        except ValueError as e:
            raise SuiValidationError(f"Invalid hex string: {e}")
    
    def verify(self, message: bytes, signature: "Signature") -> bool:
        """
        Verify an Ed25519 signature against a message.
        
        Args:
            message: The original message bytes
            signature: The Ed25519 signature to verify
            
        Returns:
            True if the signature is valid, False otherwise
            
        Raises:
            SuiValidationError: If inputs are invalid
        """
        if not isinstance(message, bytes):
            raise SuiValidationError("Message must be bytes")
        
        # Import here to avoid circular imports
        from .signature import Signature
        if not isinstance(signature, Signature):
            raise SuiValidationError("Signature must be an Ed25519 Signature")
        
        try:
            # NaCl verify method raises an exception if verification fails
            self._key.verify(message, signature.to_bytes())
            return True
        except Exception:
            # Any exception means verification failed
            return False
    
    def to_sui_address(self) -> SuiAddress:
        """
        Derive the Sui address from this Ed25519 public key.
        
        Sui address derivation for Ed25519:
        1. Take the 32-byte public key
        2. Append the Ed25519 flag byte (0x00)
        3. Hash with BLAKE2b-256
        4. Take the first 32 bytes
        5. Prepend with "0x"
        
        Returns:
            The Sui address
        """
        try:
            # Get the 32-byte public key
            public_key_bytes = self.to_bytes()
            
            # Append the Ed25519 flag byte (0x00)
            key_with_flag = public_key_bytes + bytes([self.scheme.flag_byte])
            
            # Hash with BLAKE2b-256 (32 bytes output)
            address_bytes = hashlib.blake2b(key_with_flag, digest_size=32).digest()
            
            # Convert to hex with 0x prefix
            address_hex = "0x" + address_bytes.hex()
            
            return SuiAddress.from_str(address_hex)
        except Exception as e:
            raise SuiValidationError(f"Failed to derive Sui address: {e}")
    
    def to_bytes(self) -> bytes:
        """
        Export the public key as bytes.
        
        Returns:
            The 32-byte public key
        """
        return bytes(self._key)
    
    def to_hex(self) -> str:
        """
        Export the public key as a hex string.
        
        Returns:
            The public key as hex string with 0x prefix
        """
        return "0x" + self.to_bytes().hex()
    
    @property
    def scheme(self) -> SignatureScheme:
        """
        Get the signature scheme for this key.
        
        Returns:
            SignatureScheme.ED25519
        """
        return SignatureScheme.ED25519
    
    def __str__(self) -> str:
        """String representation."""
        return f"Ed25519PublicKey(address={self.to_sui_address()})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Ed25519PublicKey("
            f"address='{self.to_sui_address()}', "
            f"scheme={self.scheme}, "
            f"hex='{self.to_hex()}'"
            f")"
        ) 