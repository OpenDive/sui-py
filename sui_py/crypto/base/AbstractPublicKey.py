from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .AbstractSignature import AbstractSignature
    from ..schemes import SignatureScheme
    from ...types.base import SuiAddress
    
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
    
    @classmethod
    @abstractmethod
    def from_base64(cls, base64_string: str) -> "AbstractPublicKey":
        """
        Create a public key from a base64 string.
        
        Args:
            base64_string: The public key as base64
            
        Returns:
            A public key instance
            
        Raises:
            ValueError: If the base64 string is invalid
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
    
    @abstractmethod
    def to_base64(self) -> str:
        """
        Export the public key as a base64 string.
        
        Returns:
            The public key as base64 string
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

