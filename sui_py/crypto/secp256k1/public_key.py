"""
Secp256k1 public key implementation using ecdsa library.
"""

import base64
import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import ecdsa
from ecdsa import VerifyingKey, SECP256k1
from ecdsa.util import sigdecode_string

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
    Secp256k1 public key implementation.
    
    This class provides secp256k1 public key functionality including
    signature verification and Sui address derivation using compressed format.
    """
    _key: VerifyingKey
    _compressed_bytes: bytes  # Store the full 33-byte compressed format
    
    def __post_init__(self):
        """Validate the public key on creation."""
        if not isinstance(self._key, VerifyingKey):
            raise SuiValidationError("Invalid secp256k1 public key")
        
        if self._key.curve != SECP256k1:
            raise SuiValidationError("Public key must use secp256k1 curve")
        
        if not isinstance(self._compressed_bytes, bytes):
            raise SuiValidationError("Compressed bytes must be bytes")
        
        if len(self._compressed_bytes) != 33:
            raise SuiValidationError("Compressed bytes must be 33 bytes")
    
    def __new__(cls, key: VerifyingKey, compressed_bytes: bytes = None):
        """Create a new PublicKey instance with proper compressed bytes."""
        if compressed_bytes is None:
            # Derive compressed bytes from the verifying key
            compressed_bytes = key.to_string("compressed")
        
        # Use object.__new__ to avoid infinite recursion
        instance = object.__new__(cls)
        object.__setattr__(instance, '_key', key)
        object.__setattr__(instance, '_compressed_bytes', compressed_bytes)
        return instance
    
    @classmethod
    def from_bytes(cls, key_bytes: bytes) -> "PublicKey":
        """
        Create a secp256k1 public key from raw bytes (compressed format).
        
        Args:
            key_bytes: The 33-byte compressed public key or 32-byte x-coordinate
            
        Returns:
            A secp256k1 public key instance
            
        Raises:
            SuiValidationError: If the key bytes are invalid
        """
        if not isinstance(key_bytes, bytes):
            raise SuiValidationError("Public key must be bytes")
        
        # Handle both compressed (33 bytes) and x-coordinate only (32 bytes) formats
        if len(key_bytes) == 32:
            # For 32-byte input, we need to try both y-coordinate parities
            # First try even y-coordinate (0x02)
            try:
                compressed_bytes = b'\x02' + key_bytes
                verifying_key = VerifyingKey.from_string(compressed_bytes, curve=SECP256k1)
                return cls(verifying_key, compressed_bytes)
            except:
                # If that fails, try odd y-coordinate (0x03)
                try:
                    compressed_bytes = b'\x03' + key_bytes
                    verifying_key = VerifyingKey.from_string(compressed_bytes, curve=SECP256k1)
                    return cls(verifying_key, compressed_bytes)
                except Exception as e:
                    raise SuiValidationError(f"Invalid secp256k1 public key x-coordinate: {e}")
        elif len(key_bytes) == 33:
            # Standard compressed format
            if key_bytes[0] not in (0x02, 0x03):
                raise SuiValidationError("Invalid compressed public key prefix")
            try:
                verifying_key = VerifyingKey.from_string(key_bytes, curve=SECP256k1)
                return cls(verifying_key, key_bytes)
            except Exception as e:
                raise SuiValidationError(f"Invalid secp256k1 public key bytes: {e}")
        else:
            raise SuiValidationError(
                f"Secp256k1 public key must be 32 or 33 bytes, got {len(key_bytes)}"
            )
    
    @classmethod
    def from_hex(cls, hex_string: str) -> "PublicKey":
        """
        Create a secp256k1 public key from a hex string.
        
        Args:
            hex_string: The public key as hex (with or without 0x prefix)
            
        Returns:
            A secp256k1 public key instance
            
        Raises:
            SuiValidationError: If the hex string is invalid
        """
        if not isinstance(hex_string, str):
            raise SuiValidationError("Hex string must be a string")
        
        # Remove 0x prefix if present
        hex_clean = hex_string.lower()
        if hex_clean.startswith("0x"):
            hex_clean = hex_clean[2:]
        
        # Validate hex format (64 or 66 hex chars for 32 or 33 bytes)
        if len(hex_clean) not in (64, 66):
            raise SuiValidationError(
                f"Secp256k1 public key hex must be 64 or 66 characters, got {len(hex_clean)}"
            )
        
        try:
            key_bytes = bytes.fromhex(hex_clean)
            return cls.from_bytes(key_bytes)
        except ValueError as e:
            raise SuiValidationError(f"Invalid hex string: {e}")
    
    def verify(self, message: bytes, signature: Signature) -> bool:
        """
        Verify a secp256k1 signature against a message.
        
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
            # ecdsa library verify method raises exception if verification fails
            # sigdecode_string expects r || s format (64 bytes)
            self._key.verify(
                signature.to_bytes(),
                message,
                sigdecode=sigdecode_string
            )
            return True
        except Exception:
            # Any exception means verification failed
            return False
    
    def to_sui_address(self) -> SuiAddress:
        """
        Derive the Sui address from this secp256k1 public key.
        
        Sui address derivation for secp256k1:
        1. Take the 32-byte x-coordinate of the public key (compressed format)
        2. Append the secp256k1 flag byte (0x01)
        3. Hash with BLAKE2b-256
        4. Take the first 32 bytes
        5. Prepend with "0x"
        
        Returns:
            The Sui address
        """
        try:
            # Get the 32-byte x-coordinate (compressed public key without prefix)
            public_key_bytes = self.to_bytes()
            
            # Append the secp256k1 flag byte (0x01)
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
        Export the public key as bytes (32-byte x-coordinate for Sui compatibility).
        
        Returns:
            The 32-byte x-coordinate of the public key
        """
        # Return just the x-coordinate (32 bytes) for Sui compatibility
        return self._compressed_bytes[1:]  # Remove the 0x02/0x03 prefix
    
    def to_compressed_bytes(self) -> bytes:
        """
        Export the full compressed public key (33 bytes).
        
        Returns:
            The 33-byte compressed public key
        """
        return self._compressed_bytes
    
    def to_hex(self) -> str:
        """
        Export the public key as a hex string (32-byte x-coordinate).
        
        Returns:
            The public key as hex string with 0x prefix
        """
        return "0x" + self.to_bytes().hex()
    
    def to_compressed_hex(self) -> str:
        """
        Export the full compressed public key as a hex string (33 bytes).
        
        Returns:
            The compressed public key as hex string with 0x prefix
        """
        return "0x" + self._compressed_bytes.hex()
    
    def to_base64(self) -> str:
        """
        Export the public key as a base64 string (32-byte x-coordinate).
        
        Returns:
            The public key as base64 string
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
        """String representation."""
        return f"Secp256k1PublicKey(address={self.to_sui_address()})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Secp256k1PublicKey("
            f"address='{self.to_sui_address()}', "
            f"scheme={self.scheme}, "
            f"hex='{self.to_hex()}'"
            f")"
        ) 