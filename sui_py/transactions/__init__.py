"""
Sui Transactions Module

This module provides comprehensive transaction building capabilities for the Sui blockchain.
It includes a fluent TransactionBuilder API for constructing Programmable Transaction Blocks (PTBs)
with full support for Move calls, object operations, coin management, and package publishing.

Core Components:
- TransactionBuilder: Main API for building transactions
- ProgrammableTransactionBlock: Container for transaction inputs and commands  
- Arguments: Type-safe argument handling (Pure, Object, Result, etc.)
- Commands: All supported transaction commands (MoveCall, Transfer, etc.)
- Complete transaction data structures for full transaction serialization

Examples:
    Basic transaction building:
    ```python
    from sui_py import TransactionBuilder
    
    tx = TransactionBuilder()
    coin = tx.object("0x123...")
    recipient = tx.pure("0xabc...")
    tx.transfer_objects([coin], recipient)
    ptb = tx.build()
    ```
    
    Complex Move call with result chaining:
    ```python
    tx = TransactionBuilder()
    pool = tx.object("0x456...")
    amount = tx.pure(1000, "u64")
    
    result = tx.move_call(
        "0x789::dex::swap",
        arguments=[pool, amount],
        type_arguments=["0x2::sui::SUI", "0xabc::token::USDC"]
    )
    
    tokens = result.single()
    tx.transfer_objects([tokens], recipient)
    ```
"""

from .builder import TransactionBuilder
from .ptb import ProgrammableTransactionBlock
from .arguments import (
    AnyArgument, PureArgument, ObjectArgument, ResultArgument, 
    GasCoinArgument, NestedResultArgument, pure, object_arg, gas_coin
)
from .commands import (
    AnyCommand, MoveCallCommand, TransferObjectsCommand, SplitCoinsCommand,
    MergeCoinsCommand, PublishCommand, UpgradeCommand, MakeMoveVecCommand
)
from .data import (
    TransactionData, TransactionDataV1, TransactionType,
    GasData, TransactionExpiration, TransactionKind, TransactionKindType
)

__all__ = [
    # Core builder
    "TransactionBuilder",
    
    # Transaction structures
    "ProgrammableTransactionBlock",
    "TransactionData", 
    "TransactionDataV1",
    "TransactionType",
    "GasData",
    "TransactionExpiration", 
    "TransactionKind",
    "TransactionKindType",
    
    # Arguments
    "AnyArgument",
    "PureArgument", 
    "ObjectArgument",
    "ResultArgument",
    "GasCoinArgument",
    "NestedResultArgument",
    "pure",
    "object_arg", 
    "gas_coin",
    
    # Commands
    "AnyCommand",
    "MoveCallCommand",
    "TransferObjectsCommand", 
    "SplitCoinsCommand",
    "MergeCoinsCommand",
    "PublishCommand",
    "UpgradeCommand",
    "MakeMoveVecCommand",
] 