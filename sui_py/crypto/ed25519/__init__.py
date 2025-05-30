"""
Ed25519 cryptographic primitives for Sui blockchain.

This module provides Ed25519 implementations using PyNaCl for optimal
performance and security.
"""

from .private_key import PrivateKey
from .public_key import PublicKey

__all__ = ["PrivateKey", "PublicKey"] 