"""
Transaction commands module with separated data structures and command envelopes.

This module implements the proper architectural separation:
- Pure data structures (MoveCall, TransferObjects, etc.) that can serialize independently
- Command envelope that wraps data structures with enum tags for PTB context
- Backward compatibility aliases for existing code
"""

from .move_call import MoveCall
from .command import Command, CommandKind

# Import old command classes from the original commands.py temporarily
# TODO: Convert these to new architecture gradually
from ..commands_old import (
    TransactionCommand,
    MoveCallCommand, 
    TransferObjectsCommand,
    SplitCoinsCommand,
    MergeCoinsCommand,
    PublishCommand,
    UpgradeCommand,
    MakeMoveVecCommand,
    AnyCommand,
    deserialize_command
)

# Re-export for backward compatibility
from .move_call import MoveCall as MoveCallCommand

__all__ = [
    # Pure data structures (new architecture)
    "MoveCall",
    
    # Command envelope (new architecture)
    "Command", 
    "CommandKind",
    
    # Backward compatibility (old architecture)
    "TransactionCommand",
    "MoveCallCommand",
    "TransferObjectsCommand", 
    "SplitCoinsCommand",
    "MergeCoinsCommand",
    "PublishCommand",
    "UpgradeCommand", 
    "MakeMoveVecCommand",
    "AnyCommand",
    "deserialize_command",
] 