"""
Abstract base class for all account types.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..crypto.base import AbstractPublicKey
    from ..crypto.signature import Signature
    from ..crypto.schemes import SignatureScheme
    from ..types.base import SuiAddress


class AbstractAccount(ABC):
    """
    Abstract base class for all account types.
    
    An account represents a cryptographic identity that can:
    - Hold a key pair (private/public keys)
    - Derive a Sui address
    - Sign messages and transactions
    - Verify signatures
    
    This abstraction supports all Sui signature schemes and can be extended
    for different account types (single key, multi-signature, etc.).
    """
    
    @property
    @abstractmethod
    def address(self) -> "SuiAddress":
        """
        Get the Sui address for this account.
        
        The address is derived from the account's public key using the
        appropriate derivation method for the signature scheme.
        
        Returns:
            The Sui address for this account
        """
        pass
    
    @property
    @abstractmethod
    def public_key(self) -> "AbstractPublicKey":
        """
        Get the public key for this account.
        
        Returns:
            The public key instance
        """
        pass
    
    @property
    @abstractmethod
    def scheme(self) -> "SignatureScheme":
        """
        Get the signature scheme used by this account.
        
        Returns:
            The signature scheme (Ed25519, Secp256k1, or Secp256r1)
        """
        pass
    
    @abstractmethod
    def sign(self, message: bytes) -> "Signature":
        """
        Sign a message with this account's private key.
        
        Args:
            message: The message bytes to sign
            
        Returns:
            The signature over the message
            
        Raises:
            SuiValidationError: If the message is invalid or signing fails
        """
        pass
    
    @abstractmethod
    def verify(self, message: bytes, signature: "Signature") -> bool:
        """
        Verify a signature against a message using this account's public key.
        
        Args:
            message: The original message bytes
            signature: The signature to verify
            
        Returns:
            True if the signature is valid, False otherwise
        """
        pass
    
    def __str__(self) -> str:
        """String representation showing scheme and address."""
        return f"{self.scheme.value}Account({self.address})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"{self.__class__.__name__}("
            f"scheme={self.scheme}, "
            f"address={self.address})"
        ) 