"""
Transaction commands module with separated data structures and command envelopes.

This module implements the proper architectural separation:
- Pure data structures (MoveCall, TransferObjects, etc.) that can serialize independently
- Command envelope that wraps data structures with enum tags for PTB context
"""

from .move_call import MoveCall
from .command import Command, CommandKind

# Re-export for backward compatibility (temporarily)
from .move_call import MoveCall as MoveCallCommand

__all__ = [
    # Pure data structures
    "MoveCall",
    
    # Command envelope
    "Command", 
    "CommandKind",
    
    # Backward compatibility
    "MoveCallCommand",
] 