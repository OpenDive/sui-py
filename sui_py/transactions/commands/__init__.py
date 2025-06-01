"""
Transaction commands module with separated data structures and command envelopes.

This module implements the proper architectural separation:
- Pure data structures (MoveCall, TransferObjects, etc.) that can serialize independently
- Command envelope that wraps data structures with enum tags for PTB context
- New argument system with CallArg for PTB inputs and TransactionArgument for command args
- Backward compatibility aliases for existing code
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

# Import old command classes from the original commands.py temporarily
# TODO: Eventually phase these out in favor of the new pure data structures
from ..commands_old import (
    TransactionCommand,
    MoveCallCommand, 
    TransferObjectsCommand,
    SplitCoinsCommand,
    MergeCoinsCommand,
    PublishCommand,
    UpgradeCommand,
    MakeMoveVecCommand,
)

__all__ = [
    # New architecture - pure data structures
    "MoveCall",
    "TransferObjects",
    "SplitCoins",
    "MergeCoins", 
    "Publish",
    "Upgrade",
    "MakeMoveVec",
    
    # New architecture - command envelope
    "Command", 
    "CommandKind",
    "AnyCommand",
    
    # New argument system
    "CallArg", "CallArgKind", "PureCallArg", "ObjectCallArg", "InputCallArg",
    "TransactionArgument", "TransactionArgumentKind",
    "GasCoinTransactionArgument", "InputTransactionArgument", 
    "ResultTransactionArgument", "NestedResultTransactionArgument",
    
    # Backward compatibility - old command classes
    "TransactionCommand",
    "MoveCallCommand", 
    "TransferObjectsCommand",
    "SplitCoinsCommand", 
    "MergeCoinsCommand",
    "PublishCommand",
    "UpgradeCommand", 
    "MakeMoveVecCommand",
]

# Backward compatibility aliases
MoveCallCommand = MoveCall
TransferObjectsCommand = TransferObjects
SplitCoinsCommand = SplitCoins
MergeCoinsCommand = MergeCoins
PublishCommand = Publish
UpgradeCommand = Upgrade
MakeMoveVecCommand = MakeMoveVec

# Backward compatibility function - delegates to Command.deserialize
def deserialize_command(deserializer):
    """Backward compatibility function - use Command.deserialize() instead."""
    return Command.deserialize(deserializer) 