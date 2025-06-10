"""
SuiPy - A lightweight, high-performance Python SDK for the Sui blockchain.

Async-first design for optimal performance with I/O-bound blockchain operations.
"""

__version__ = "0.1.0"
__author__ = "SuiPy Team"

# Show welcome message on first import
import os
import sys

_WELCOME_SHOWN_FILE = os.path.expanduser("~/.suipy_welcome_shown")

if not os.path.exists(_WELCOME_SHOWN_FILE) and not os.environ.get("SUIPY_SKIP_WELCOME"):
    try:
        from ._ascii_art import display_install_message
        display_install_message()
        # Create marker file to avoid showing again
        try:
            with open(_WELCOME_SHOWN_FILE, "w") as f:
                f.write("1")
        except:
            pass  # Ignore file creation errors
    except ImportError:
        pass

from .client import SuiClient
from .exceptions import SuiError, SuiRPCError, SuiValidationError
from .types import (
    # Base types
    SuiAddress, ObjectID, ObjectRef, TransactionDigest, Base64, Hex,
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
    # Unified signature
    Signature,
    # Ed25519 implementations
    Ed25519PrivateKey, Ed25519PublicKey,
    # Secp256k1 implementations
    Secp256k1PrivateKey, Secp256k1PublicKey,
    # Factory functions
    create_private_key, import_private_key
)

# Transaction building system
from .transactions import (
    # Builder
    TransactionBuilder,
    # PTB
    ProgrammableTransactionBlock,
    # Arguments
    PureArgument, ObjectArgument, ResultArgument, GasCoinArgument,
    # Commands
    MoveCall, TransferObjects, SplitCoins,
    MergeCoins, Publish, Upgrade, MakeMoveVec, Command
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
    "ObjectRef",
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
    "Signature",
    "Ed25519PrivateKey",
    "Ed25519PublicKey",
    "Secp256k1PrivateKey",
    "Secp256k1PublicKey",
    "create_private_key",
    "import_private_key",
    
    # Transaction building
    "TransactionBuilder",
    "ProgrammableTransactionBlock",
    "PureArgument",
    "ObjectArgument", 
    "ResultArgument",
    "GasCoinArgument",
    "MoveCall",
    "TransferObjects",
    "SplitCoins",
    "MergeCoins",
    "Publish",
    "Upgrade", 
    "MakeMoveVec",
    "Command",
] 