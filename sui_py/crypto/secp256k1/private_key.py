"""
Secp256k1 private key implementation using ecdsa library.
"""

import base64
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING

import ecdsa
from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigencode_string

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
    Secp256k1 private key implementation.
    
    This class provides secp256k1 private key functionality including
    key generation, deterministic signing, and serialization operations.
    """
    _key: SigningKey
    
    def __post_init__(self):
        """Validate the private key on creation."""
        if not isinstance(self._key, SigningKey):
            raise SuiValidationError("Invalid secp256k1 private key")
        
        if self._key.curve != SECP256k1:
            raise SuiValidationError("Private key must use secp256k1 curve")
    
    @classmethod
    def generate(cls) -> "PrivateKey":
        """
        Generate a new random secp256k1 private key.
        
        Returns:
            A new secp256k1 private key instance
        """
        # Generate a valid private key (1 to n-1 where n is curve order)
        while True:
            private_key_bytes = secrets.token_bytes(32)
            # Ensure the private key is in valid range [1, n-1]
            private_key_int = int.from_bytes(private_key_bytes, 'big')
            if 1 <= private_key_int < SECP256k1.order:
                break
        
        signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        return cls(signing_key)
    
    @classmethod
    def from_bytes(cls, key_bytes: bytes) -> "PrivateKey":
        """
        Create a secp256k1 private key from raw bytes.
        
        Args:
            key_bytes: The 32-byte private key
            
        Returns:
            A secp256k1 private key instance
            
        Raises:
            SuiValidationError: If the key bytes are invalid
        """
        if not isinstance(key_bytes, bytes):
            raise SuiValidationError("Private key must be bytes")
        
        if len(key_bytes) != 32:
            raise SuiValidationError(
                f"Secp256k1 private key must be 32 bytes, got {len(key_bytes)}"
            )
        
        # Validate private key is in valid range [1, n-1]
        private_key_int = int.from_bytes(key_bytes, 'big')
        if private_key_int == 0:
            raise SuiValidationError("Private key cannot be zero")
        if private_key_int >= SECP256k1.order:
            raise SuiValidationError("Private key must be less than curve order")
        
        try:
            signing_key = SigningKey.from_string(key_bytes, curve=SECP256k1)
            return cls(signing_key)
        except Exception as e:
            raise SuiValidationError(f"Invalid secp256k1 private key bytes: {e}")
    
    @classmethod
    def from_hex(cls, hex_string: str) -> "PrivateKey":
        """
        Create a secp256k1 private key from a hex string.
        
        Args:
            hex_string: The private key as hex (with or without 0x prefix)
            
        Returns:
            A secp256k1 private key instance
            
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
                f"Secp256k1 private key hex must be 64 characters, got {len(hex_clean)}"
            )
        
        try:
            key_bytes = bytes.fromhex(hex_clean)
            return cls.from_bytes(key_bytes)
        except ValueError as e:
            raise SuiValidationError(f"Invalid hex string: {e}")
    
    def public_key(self) -> PublicKey:
        """
        Get the corresponding secp256k1 public key.
        
        Returns:
            The secp256k1 public key derived from this private key
        """
        verifying_key = self._key.get_verifying_key()
        compressed_bytes = verifying_key.to_string("compressed")
        return PublicKey(verifying_key, compressed_bytes)
    
    def sign(self, message: bytes) -> Signature:
        """
        Sign a message with this secp256k1 private key using deterministic signatures.
        
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
            # Use deterministic signatures (RFC 6979) for consistency
            # sigencode_string returns r || s as 64 bytes (32 each)
            signature_bytes = self._key.sign_deterministic(
                message, 
                sigencode=sigencode_string
            )
            
            # Ensure we got exactly 64 bytes (32 for r, 32 for s)
            if len(signature_bytes) != 64:
                raise SuiValidationError(f"Expected 64-byte signature, got {len(signature_bytes)}")
            
            return Signature(signature_bytes, SignatureScheme.SECP256K1)
        except Exception as e:
            raise SuiValidationError(f"Failed to sign message: {e}")
    
    def to_bytes(self) -> bytes:
        """
        Export the private key as bytes.
        
        Returns:
            The 32-byte private key
        """
        return self._key.to_string()
    
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
            SignatureScheme.SECP256K1
        """
        return SignatureScheme.SECP256K1
    
    def __str__(self) -> str:
        """String representation (does not expose private key)."""
        return f"Secp256k1PrivateKey(address={self.public_key().to_sui_address()})"
    
    def __repr__(self) -> str:
        """Detailed representation (does not expose private key)."""
        return (
            f"Secp256k1PrivateKey("
            f"address='{self.public_key().to_sui_address()}', "
            f"scheme={self.scheme}"
            f")"
        ) 