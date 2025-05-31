"""
Command envelope and kind definitions.

This module defines the Command wrapper that adds enum tags to pure data structures,
following the architectural pattern from the C# Unity SDK.
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Union
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer
from .move_call import MoveCall


class CommandKind(IntEnum):
    """
    Enum representation of Sui command types.
    
    These values correspond to the BCS enum variant tags used in serialization.
    """
    MoveCall = 0
    TransferObjects = 1
    SplitCoins = 2
    MergeCoins = 3
    Publish = 4
    Upgrade = 5
    MakeMoveVec = 6


# Type alias for all command data types
CommandData = Union[MoveCall]  # Will expand as we add more command types


@dataclass
class Command(BcsSerializable):
    """
    Command envelope that wraps command data structures with BCS enum tags.
    
    This follows the C# Unity SDK pattern where:
    - Command data structures (MoveCall, etc.) serialize just their data
    - Command envelope adds the enum tag for PTB context
    
    Example:
        move_call = MoveCall(package="0x2", module="coin", function="split", ...)
        command = Command(CommandKind.MoveCall, move_call)
        
        # move_call.serialize() → just the MoveCall data
        # command.serialize() → tag + MoveCall data
    """
    kind: CommandKind
    data: CommandData
    
    def __post_init__(self):
        """Validate command kind matches data type."""
        if self.kind == CommandKind.MoveCall and not isinstance(self.data, MoveCall):
            raise ValueError("CommandKind.MoveCall requires MoveCall data")
        # TODO: Add validation for other command types as we implement them
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize command with BCS enum format: tag byte + data.
        
        This matches the C# Command.Serialize() behavior:
        1. Write the command kind as u8
        2. Serialize the wrapped data structure
        """
        serializer.write_u8(self.kind.value)
        self.data.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """
        Deserialize command from BCS enum format.
        
        Reads the tag byte and delegates to appropriate data structure deserializer.
        """
        tag = deserializer.read_u8()
        
        if tag == CommandKind.MoveCall.value:
            data = MoveCall.deserialize(deserializer)
            return cls(CommandKind.MoveCall, data)
        else:
            # TODO: Add other command types as we implement them
            raise ValueError(f"Unknown command tag: {tag}")
    
    @classmethod 
    def move_call(cls, move_call: MoveCall) -> "Command":
        """Convenience constructor for MoveCall commands."""
        return cls(CommandKind.MoveCall, move_call) 