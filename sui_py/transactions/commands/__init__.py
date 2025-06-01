"""
Transaction commands module with separated data structures and command envelopes.

This module implements the proper architectural separation:
- Pure data structures (MoveCall, TransferObjects, etc.) that can serialize independently
- Command envelope that wraps data structures with enum tags for PTB context
- New argument system with CallArg for PTB inputs and TransactionArgument for command args
"""

from .move_call import MoveCall
from .transfer_objects import TransferObjects
from .split_coins import SplitCoins
from .merge_coins import MergeCoins
from .publish import Publish
from .upgrade import Upgrade
from .make_move_vec import MakeMoveVec
from .command import Command, CommandKind, AnyCommand
from ..call_arg import CallArg, CallArgKind, PureCallArg, ObjectCallArg, InputCallArg
from ..transaction_argument import (
    TransactionArgument, TransactionArgumentKind,
    GasCoinTransactionArgument, InputTransactionArgument, 
    ResultTransactionArgument, NestedResultTransactionArgument
)

__all__ = [
    # Pure data structures
    "MoveCall",
    "TransferObjects",
    "SplitCoins",
    "MergeCoins", 
    "Publish",
    "Upgrade",
    "MakeMoveVec",
    
    # Command envelope
    "Command", 
    "CommandKind",
    "AnyCommand",
    
    # Argument system
    "CallArg", "CallArgKind", "PureCallArg", "ObjectCallArg", "InputCallArg",
    "TransactionArgument", "TransactionArgumentKind",
    "GasCoinTransactionArgument", "InputTransactionArgument", 
    "ResultTransactionArgument", "NestedResultTransactionArgument",
] 