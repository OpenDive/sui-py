"""
Abstract base classes for cryptographic primitives.

These classes define the common interface that all signature scheme
implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types.base import SuiAddress
    from .schemes import SignatureScheme


class AbstractPrivateKey(ABC):
    """
    Abstract base class for private keys across all signature schemes.
    """
    
    @classmethod
    @abstractmethod
    def generate(cls) -> "AbstractPrivateKey":
        """
        Generate a new random private key.
        
        Returns:
            A new private key instance
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_bytes(cls, key_bytes: bytes) -> "AbstractPrivateKey":
        """
        Create a private key from raw bytes.
        
        Args:
            key_bytes: The private key bytes
            
        Returns:
            A private key instance
            
        Raises:
            ValueError: If the key bytes are invalid
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_hex(cls, hex_string: str) -> "AbstractPrivateKey":
        """
        Create a private key from a hex string.
        
        Args:
            hex_string: The private key as hex (with or without 0x prefix)
            
        Returns:
            A private key instance
            
        Raises:
            ValueError: If the hex string is invalid
        """
        pass
    
    @abstractmethod
    def public_key(self) -> "AbstractPublicKey":
        """
        Get the corresponding public key.
        
        Returns:
            The public key derived from this private key
        """
        pass
    
    @abstractmethod
    def sign(self, message: bytes) -> "AbstractSignature":
        """
        Sign a message with this private key.
        
        Args:
            message: The message bytes to sign
            
        Returns:
            The signature
        """
        pass
    
    @abstractmethod
    def to_bytes(self) -> bytes:
        """
        Export the private key as bytes.
        
        Returns:
            The private key bytes
        """
        pass
    
    @abstractmethod
    def to_hex(self) -> str:
        """
        Export the private key as a hex string.
        
        Returns:
            The private key as hex string with 0x prefix
        """
        pass
    
    @property
    @abstractmethod
    def scheme(self) -> "SignatureScheme":
        """
        Get the signature scheme for this key.
        
        Returns:
            The signature scheme
        """
        pass


class AbstractPublicKey(ABC):
    """
    Abstract base class for public keys across all signature schemes.
    """
    
    @classmethod
    @abstractmethod
    def from_bytes(cls, key_bytes: bytes) -> "AbstractPublicKey":
        """
        Create a public key from raw bytes.
        
        Args:
            key_bytes: The public key bytes
            
        Returns:
            A public key instance
            
        Raises:
            ValueError: If the key bytes are invalid
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_hex(cls, hex_string: str) -> "AbstractPublicKey":
        """
        Create a public key from a hex string.
        
        Args:
            hex_string: The public key as hex (with or without 0x prefix)
            
        Returns:
            A public key instance
            
        Raises:
            ValueError: If the hex string is invalid
        """
        pass
    
    @abstractmethod
    def verify(self, message: bytes, signature: "AbstractSignature") -> bool:
        """
        Verify a signature against a message.
        
        Args:
            message: The original message bytes
            signature: The signature to verify
            
        Returns:
            True if the signature is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def to_sui_address(self) -> "SuiAddress":
        """
        Derive the Sui address from this public key.
        
        Returns:
            The Sui address
        """
        pass
    
    @abstractmethod
    def to_bytes(self) -> bytes:
        """
        Export the public key as bytes.
        
        Returns:
            The public key bytes
        """
        pass
    
    @abstractmethod
    def to_hex(self) -> str:
        """
        Export the public key as a hex string.
        
        Returns:
            The public key as hex string with 0x prefix
        """
        pass
    
    @property
    @abstractmethod
    def scheme(self) -> "SignatureScheme":
        """
        Get the signature scheme for this key.
        
        Returns:
            The signature scheme
        """
        pass


class AbstractSignature(ABC):
    """
    Abstract base class for signatures across all signature schemes.
    """
    
    @classmethod
    @abstractmethod
    def from_bytes(cls, signature_bytes: bytes) -> "AbstractSignature":
        """
        Create a signature from raw bytes.
        
        Args:
            signature_bytes: The signature bytes
            
        Returns:
            A signature instance
            
        Raises:
            ValueError: If the signature bytes are invalid
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_hex(cls, hex_string: str) -> "AbstractSignature":
        """
        Create a signature from a hex string.
        
        Args:
            hex_string: The signature as hex (with or without 0x prefix)
            
        Returns:
            A signature instance
            
        Raises:
            ValueError: If the hex string is invalid
        """
        pass
    
    @abstractmethod
    def to_bytes(self) -> bytes:
        """
        Export the signature as bytes.
        
        Returns:
            The signature bytes
        """
        pass
    
    @abstractmethod
    def to_hex(self) -> str:
        """
        Export the signature as a hex string.
        
        Returns:
            The signature as hex string with 0x prefix
        """
        pass
    
    @property
    @abstractmethod
    def scheme(self) -> "SignatureScheme":
        """
        Get the signature scheme for this signature.
        
        Returns:
            The signature scheme
        """
        pass 