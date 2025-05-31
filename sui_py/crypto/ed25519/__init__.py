"""
Ed25519 cryptographic primitives for Sui blockchain.

This module provides Ed25519 implementations using PyNaCl for optimal
performance and security.
"""

from .private_key import PrivateKey as Ed25519PrivateKey
from .public_key import PublicKey as Ed25519PublicKey

# Also export the short names for convenience
from .private_key import PrivateKey
from .public_key import PublicKey

__all__ = ["Ed25519PrivateKey", "Ed25519PublicKey", "PrivateKey", "PublicKey"] 