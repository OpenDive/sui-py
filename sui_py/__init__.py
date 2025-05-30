"""
SuiPy - A lightweight, high-performance Python SDK for the Sui blockchain.

Async-first design for optimal performance with I/O-bound blockchain operations.
"""

__version__ = "0.1.0"
__author__ = "SuiPy Team"

from .client import SuiClient
from .exceptions import SuiError, SuiRPCError, SuiValidationError
from .types import (
    # Base types
    SuiAddress, ObjectID, TransactionDigest, Base64, Hex,
    # Coin types
    Balance, Coin, SuiCoinMetadata, Supply,
    # Pagination
    Page,
    # Extended API enums
    EventType, ObjectDataOptions,
    # Dynamic fields
    DynamicFieldName, DynamicFieldInfo,
    # Objects
    ObjectOwner, SuiObjectData, SuiObjectResponse,
    # Events
    SuiEvent,
    # Transactions
    TransactionBlockResponseOptions, SuiTransactionBlock, SuiTransactionBlockResponse,
    # Query filters
    EventFilter, TransactionFilter
)

# Crypto primitives
from .crypto import (
    # Core abstractions
    SignatureScheme, AbstractPrivateKey, AbstractPublicKey, AbstractSignature,
    # Ed25519 implementations
    Ed25519PrivateKey, Ed25519PublicKey, Ed25519Signature,
    # Factory functions
    create_private_key, import_private_key
)

__all__ = [
    # Client
    "SuiClient",
    
    # Exceptions
    "SuiError", 
    "SuiRPCError",
    "SuiValidationError",
    
    # Base types
    "SuiAddress",
    "ObjectID", 
    "TransactionDigest",
    "Base64",
    "Hex",
    
    # Coin types
    "Balance",
    "Coin",
    "SuiCoinMetadata", 
    "Supply",
    
    # Pagination
    "Page",
    
    # Extended API enums
    "EventType",
    "ObjectDataOptions",
    
    # Dynamic fields
    "DynamicFieldName",
    "DynamicFieldInfo",
    
    # Objects
    "ObjectOwner",
    "SuiObjectData",
    "SuiObjectResponse",
    
    # Events
    "SuiEvent",
    
    # Transactions
    "TransactionBlockResponseOptions",
    "SuiTransactionBlock",
    "SuiTransactionBlockResponse",
    
    # Query filters
    "EventFilter",
    "TransactionFilter",
    
    # Crypto primitives
    "SignatureScheme",
    "AbstractPrivateKey",
    "AbstractPublicKey", 
    "AbstractSignature",
    "Ed25519PrivateKey",
    "Ed25519PublicKey",
    "Ed25519Signature",
    "create_private_key",
    "import_private_key",
] 