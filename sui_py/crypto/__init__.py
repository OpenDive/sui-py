"""
Cryptographic primitives for Sui blockchain operations.

This module provides unified interfaces for different signature schemes
supported by the Sui blockchain, including Ed25519, Secp256k1, and Secp256r1.
"""

from .schemes import SignatureScheme
from .base import AbstractPrivateKey, AbstractPublicKey, AbstractSignature
from .signature import Signature

# Ed25519 implementations
from .ed25519 import (
    PrivateKey as Ed25519PrivateKey,
    PublicKey as Ed25519PublicKey
)

# Secp256k1 implementations
from .secp256k1 import (
    PrivateKey as Secp256k1PrivateKey,
    PublicKey as Secp256k1PublicKey
)

__all__ = [
    # Core abstractions
    "SignatureScheme",
    "AbstractPrivateKey",
    "AbstractPublicKey", 
    "AbstractSignature",
    
    # Unified signature
    "Signature",
    
    # Ed25519 implementations
    "Ed25519PrivateKey",
    "Ed25519PublicKey",
    
    # Secp256k1 implementations
    "Secp256k1PrivateKey",
    "Secp256k1PublicKey",
    
    # Factory functions
    "create_private_key",
    "import_private_key",
]


def create_private_key(scheme: SignatureScheme) -> AbstractPrivateKey:
    """
    Create a new private key for the specified signature scheme.
    
    Args:
        scheme: The signature scheme to use
        
    Returns:
        A new private key instance
        
    Raises:
        NotImplementedError: If the scheme is not yet supported
    """
    if scheme == SignatureScheme.ED25519:
        return Ed25519PrivateKey.generate()
    elif scheme == SignatureScheme.SECP256K1:
        return Secp256k1PrivateKey.generate()
    elif scheme == SignatureScheme.SECP256R1:
        raise NotImplementedError("Secp256r1 support coming soon")
    else:
        raise ValueError(f"Unknown signature scheme: {scheme}")


def import_private_key(private_key_bytes: bytes, scheme: SignatureScheme) -> AbstractPrivateKey:
    """
    Import a private key from bytes for the specified signature scheme.
    
    Args:
        private_key_bytes: The private key bytes
        scheme: The signature scheme to use
        
    Returns:
        A private key instance
        
    Raises:
        NotImplementedError: If the scheme is not yet supported
    """
    if scheme == SignatureScheme.ED25519:
        return Ed25519PrivateKey.from_bytes(private_key_bytes)
    elif scheme == SignatureScheme.SECP256K1:
        return Secp256k1PrivateKey.from_bytes(private_key_bytes)
    elif scheme == SignatureScheme.SECP256R1:
        raise NotImplementedError("Secp256r1 support coming soon")
    else:
        raise ValueError(f"Unknown signature scheme: {scheme}") 