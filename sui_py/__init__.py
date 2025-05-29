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
] 