"""
Ed25519 private key implementation using PyNaCl.
"""

import base64
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING

import nacl.signing
import nacl.encoding

from ...exceptions import SuiValidationError
from ..base import AbstractPrivateKey
from ..schemes import SignatureScheme
from ..signature import Signature
from .public_key import PublicKey

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class PrivateKey(AbstractPrivateKey):
    """
    Ed25519 private key implementation.
    
    This class provides Ed25519 private key functionality including
    key generation, signing, and serialization operations.
    """
    _key: nacl.signing.SigningKey
    
    def __post_init__(self):
        """Validate the private key on creation."""
        if not isinstance(self._key, nacl.signing.SigningKey):
            raise SuiValidationError("Invalid Ed25519 private key")
    
    @classmethod
    def generate(cls) -> "PrivateKey":
        """
        Generate a new random Ed25519 private key.
        
        Returns:
            A new Ed25519 private key instance
        """
        # Generate 32 bytes of cryptographically secure random data
        private_key_bytes = secrets.token_bytes(32)
        signing_key = nacl.signing.SigningKey(private_key_bytes)
        return cls(signing_key)
    
    @classmethod
    def from_bytes(cls, key_bytes: bytes) -> "PrivateKey":
        """
        Create an Ed25519 private key from raw bytes.
        
        Args:
            key_bytes: The 32-byte private key
            
        Returns:
            An Ed25519 private key instance
            
        Raises:
            SuiValidationError: If the key bytes are invalid
        """
        if not isinstance(key_bytes, bytes):
            raise SuiValidationError("Private key must be bytes")
        
        if len(key_bytes) != 32:
            raise SuiValidationError(
                f"Ed25519 private key must be 32 bytes, got {len(key_bytes)}"
            )
        
        try:
            signing_key = nacl.signing.SigningKey(key_bytes)
            return cls(signing_key)
        except Exception as e:
            raise SuiValidationError(f"Invalid Ed25519 private key bytes: {e}")
    
    @classmethod
    def from_hex(cls, hex_string: str) -> "PrivateKey":
        """
        Create an Ed25519 private key from a hex string.
        
        Args:
            hex_string: The private key as hex (with or without 0x prefix)
            
        Returns:
            An Ed25519 private key instance
            
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
                f"Ed25519 private key hex must be 64 characters, got {len(hex_clean)}"
            )
        
        try:
            key_bytes = bytes.fromhex(hex_clean)
            return cls.from_bytes(key_bytes)
        except ValueError as e:
            raise SuiValidationError(f"Invalid hex string: {e}")
    
    @classmethod
    def from_base64(cls, base64_string: str) -> "PrivateKey":
        """
        Create an Ed25519 private key from a base64 string.
        
        Args:
            base64_string: The private key as base64
            
        Returns:
            An Ed25519 private key instance
            
        Raises:
            SuiValidationError: If the base64 string is invalid
        """
        if not isinstance(base64_string, str):
            raise SuiValidationError("Base64 string must be a string")
        
        try:
            key_bytes = base64.b64decode(base64_string)
            return cls.from_bytes(key_bytes)
        except Exception as e:
            raise SuiValidationError(f"Invalid base64 string: {e}")
    
    def public_key(self) -> PublicKey:
        """
        Get the corresponding Ed25519 public key.
        
        Returns:
            The Ed25519 public key derived from this private key
        """
        verify_key = self._key.verify_key
        return PublicKey(verify_key)
    
    def sign(self, message: bytes) -> Signature:
        """
        Sign a message with this Ed25519 private key.
        
        Args:
            message: The message bytes to sign
            
        Returns:
            The signature
            
        Raises:
            SuiValidationError: If the message is invalid
        """
        if not isinstance(message, bytes):
            raise SuiValidationError("Message must be bytes")
        
        try:
            # NaCl produces a 64-byte signature
            signed_message = self._key.sign(message)
            signature_bytes = signed_message.signature
            return Signature(signature_bytes, SignatureScheme.ED25519)
        except Exception as e:
            raise SuiValidationError(f"Failed to sign message: {e}")
    
    def to_bytes(self) -> bytes:
        """
        Export the private key as bytes.
        
        Returns:
            The 32-byte private key
        """
        return bytes(self._key)
    
    def to_hex(self) -> str:
        """
        Export the private key as a hex string.
        
        Returns:
            The private key as hex string with 0x prefix
        """
        return "0x" + self.to_bytes().hex()
    
    def to_base64(self) -> str:
        """
        Export the private key as a base64 string.
        
        Returns:
            The private key as base64 string
        """
        return base64.b64encode(self.to_bytes()).decode('utf-8')
    
    @property
    def scheme(self) -> SignatureScheme:
        """
        Get the signature scheme for this key.
        
        Returns:
            SignatureScheme.ED25519
        """
        return SignatureScheme.ED25519
    
    def __str__(self) -> str:
        """String representation (does not expose private key)."""
        return f"Ed25519PrivateKey(address={self.public_key().to_sui_address()})"
    
    def __repr__(self) -> str:
        """Detailed representation (does not expose private key)."""
        return (
            f"Ed25519PrivateKey("
            f"address='{self.public_key().to_sui_address()}', "
            f"scheme={self.scheme}"
            f")"
        ) 