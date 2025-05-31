"""
Ed25519 public key implementation using PyNaCl.
"""

import base64
import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import nacl.signing
import nacl.encoding

from ...exceptions import SuiValidationError
from ...types.base import SuiAddress
from ..base import AbstractPublicKey
from ..schemes import SignatureScheme
from ..signature import Signature

if TYPE_CHECKING:
    pass


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
    
    @classmethod
    def from_base64(cls, base64_string: str) -> "PublicKey":
        """
        Create an Ed25519 public key from a base64 string.
        
        Args:
            base64_string: The public key as base64
            
        Returns:
            An Ed25519 public key instance
            
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
    
    def verify(self, message: bytes, signature: Signature) -> bool:
        """
        Verify a signature against a message.
        
        Args:
            message: The original message bytes
            signature: The signature to verify
            
        Returns:
            True if the signature is valid, False otherwise
            
        Raises:
            SuiValidationError: If inputs are invalid
        """
        if not isinstance(message, bytes):
            raise SuiValidationError("Message must be bytes")
        
        if not isinstance(signature, Signature):
            raise SuiValidationError("Signature must be a Signature instance")
        
        # Verify that the signature scheme matches this key's scheme
        if signature.scheme != self.scheme:
            raise SuiValidationError(
                f"Signature scheme {signature.scheme} does not match key scheme {self.scheme}"
            )
        
        try:
            # NaCl verify method raises an exception if verification fails
            self._key.verify(message, signature.to_bytes())
            return True
        except Exception:
            # Any exception means verification failed
            return False
    
    def to_sui_bytes(self) -> bytes:
        """
        Return the Sui representation of the public key.
        
        A Sui public key is formed by the concatenation of the scheme flag 
        with the raw bytes of the public key: [flag_byte, ...public_key_bytes]
        
        Returns:
            The 33-byte Sui public key (flag + raw key)
        """
        public_key_bytes = self.to_bytes()
        sui_bytes = bytes([self.scheme.flag_byte]) + public_key_bytes
        return sui_bytes
    
    def to_sui_public_key(self) -> str:
        """
        Return the Sui representation of the public key encoded in base64.
        
        A Sui public key is formed by the concatenation of the scheme flag 
        with the raw bytes of the public key, then base64 encoded.
        
        Returns:
            The Sui public key as base64 string
        """
        return base64.b64encode(self.to_sui_bytes()).decode('utf-8')
    
    def to_sui_address(self) -> SuiAddress:
        """
        Derive the Sui address from this Ed25519 public key.
        
        Sui address derivation for Ed25519:
        1. Create sui_bytes: [flag_byte, ...public_key_bytes] (33 bytes)
        2. Hash with BLAKE2b-256 (32 bytes output)
        3. Convert to hex with 0x prefix
        
        Returns:
            The Sui address
        """
        try:
            # Get the Sui bytes (flag + public key, 33 bytes total)
            sui_bytes = self.to_sui_bytes()
            
            # Hash with BLAKE2b-256 (32 bytes output)
            address_bytes = hashlib.blake2b(sui_bytes, digest_size=32).digest()
            
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
    
    def to_base64(self) -> str:
        """
        Export the public key as a base64 string.
        
        Returns:
            The public key as base64 string
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