from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .AbstractPublicKey import AbstractPublicKey
    from ..schemes import SignatureScheme

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