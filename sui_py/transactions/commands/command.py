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


# For now, we'll import the old command classes for other types
# TODO: Convert these to pure data structures like MoveCall
from ..commands_old import (
    TransferObjectsCommand, SplitCoinsCommand, MergeCoinsCommand,
    PublishCommand, UpgradeCommand, MakeMoveVecCommand
)

# Union type for all command data types
CommandData = Union[
    MoveCall,  # New pure data structure
    # Old command classes (temporary until converted)
    TransferObjectsCommand,
    SplitCoinsCommand, 
    MergeCoinsCommand,
    PublishCommand,
    UpgradeCommand,
    MakeMoveVecCommand
]


@dataclass
class Command(BcsSerializable):
    """
    Command envelope that wraps pure data structures with enum tags.
    
    This handles all command serialization/deserialization internally,
    eliminating the need for external deserialize_command functions.
    """
    data: CommandData
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize with enum tag followed by command data."""
        if isinstance(self.data, MoveCall):
            serializer.write_u8(CommandKind.MoveCall)
            self.data.serialize(serializer)
        elif isinstance(self.data, TransferObjectsCommand):
            serializer.write_u8(CommandKind.TransferObjects)
            self.data.serialize_command_data(serializer)
        elif isinstance(self.data, SplitCoinsCommand):
            serializer.write_u8(CommandKind.SplitCoins)
            self.data.serialize_command_data(serializer)
        elif isinstance(self.data, MergeCoinsCommand):
            serializer.write_u8(CommandKind.MergeCoins)
            self.data.serialize_command_data(serializer)
        elif isinstance(self.data, PublishCommand):
            serializer.write_u8(CommandKind.Publish)
            self.data.serialize_command_data(serializer)
        elif isinstance(self.data, UpgradeCommand):
            serializer.write_u8(CommandKind.Upgrade)
            self.data.serialize_command_data(serializer)
        elif isinstance(self.data, MakeMoveVecCommand):
            serializer.write_u8(CommandKind.MakeMoveVec)
            self.data.serialize_command_data(serializer)
        else:
            raise ValueError(f"Unknown command type: {type(self.data)}")
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes - handles all command types internally."""
        tag = deserializer.read_u8()
        
        if tag == CommandKind.MoveCall:
            data = MoveCall.deserialize(deserializer)
        elif tag == CommandKind.TransferObjects:
            data = TransferObjectsCommand.deserialize(deserializer)
        elif tag == CommandKind.SplitCoins:
            data = SplitCoinsCommand.deserialize(deserializer)
        elif tag == CommandKind.MergeCoins:
            data = MergeCoinsCommand.deserialize(deserializer)
        elif tag == CommandKind.Publish:
            data = PublishCommand.deserialize(deserializer)
        elif tag == CommandKind.Upgrade:
            data = UpgradeCommand.deserialize(deserializer)
        elif tag == CommandKind.MakeMoveVec:
            data = MakeMoveVecCommand.deserialize(deserializer)
        else:
            raise ValueError(f"Unknown command tag: {tag}")
        
        return cls(data=data)
    
    @classmethod
    def move_call(cls, package: str, module: str, function: str, 
                  type_arguments: list = None, arguments: list = None) -> "Command":
        """Create a MoveCall command."""
        move_call = MoveCall(
            package=package,
            module=module, 
            function=function,
            type_arguments=type_arguments or [],
            arguments=arguments or []
        )
        return cls(data=move_call)
    
    @classmethod
    def transfer_objects(cls, objects: list, recipient) -> "Command":
        """Create a TransferObjects command."""
        transfer = TransferObjectsCommand(objects=objects, recipient=recipient)
        return cls(data=transfer)
    
    @classmethod
    def split_coins(cls, coin, amounts: list) -> "Command":
        """Create a SplitCoins command."""
        split = SplitCoinsCommand(coin=coin, amounts=amounts)
        return cls(data=split)
    
    @classmethod
    def merge_coins(cls, destination, sources: list) -> "Command":
        """Create a MergeCoins command."""
        merge = MergeCoinsCommand(destination=destination, sources=sources)
        return cls(data=merge)
    
    @classmethod
    def publish(cls, modules: list, dependencies: list) -> "Command":
        """Create a Publish command."""
        publish = PublishCommand(modules=modules, dependencies=dependencies)
        return cls(data=publish)
    
    @classmethod
    def upgrade(cls, modules: list, dependencies: list, package: str, ticket) -> "Command":
        """Create an Upgrade command."""
        upgrade = UpgradeCommand(
            modules=modules, 
            dependencies=dependencies,
            package=package,
            ticket=ticket
        )
        return cls(data=upgrade)
    
    @classmethod
    def make_move_vec(cls, type_argument: str = None, elements: list = None) -> "Command":
        """Create a MakeMoveVec command."""
        make_vec = MakeMoveVecCommand(
            type_argument=type_argument,
            elements=elements or []
        )
        return cls(data=make_vec)


# Type alias for backward compatibility
AnyCommand = Command 