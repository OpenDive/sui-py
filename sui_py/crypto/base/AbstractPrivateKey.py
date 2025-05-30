from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .AbstractPublicKey import AbstractPublicKey
    from .AbstractSignature import AbstractSignature
    from ..schemes import SignatureScheme

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

