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
from .transfer_objects import TransferObjects
from .split_coins import SplitCoins
from .merge_coins import MergeCoins
from .publish import Publish
from .upgrade import Upgrade
from .make_move_vec import MakeMoveVec

from ...utils.logging import setup_logging, get_logger
import logging

setup_logging(level=logging.DEBUG, use_emojis=True)
logger = get_logger("sui_py.transactions.commands.command.Command")

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


# Union type for all command data types - now all pure data structures
CommandData = Union[
    MoveCall,
    TransferObjects,
    SplitCoins, 
    MergeCoins,
    Publish,
    Upgrade,
    MakeMoveVec
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
            logger.debug(f"Serializing MoveCall Command: {self.data}")
            serializer.write_u8(CommandKind.MoveCall)
            self.data.serialize(serializer)
        elif isinstance(self.data, TransferObjects):
            logger.debug(f"Serializing TransferObjects Command: {self.data}")
            serializer.write_u8(CommandKind.TransferObjects)
            self.data.serialize(serializer)
        elif isinstance(self.data, SplitCoins):
            logger.debug(f"Serializing SplitCoins Command: {self.data}")
            serializer.write_u8(CommandKind.SplitCoins)
            self.data.serialize(serializer)
        elif isinstance(self.data, MergeCoins):
            logger.debug(f"Serializing MergeCoins Command: {self.data}")
            serializer.write_u8(CommandKind.MergeCoins)
            self.data.serialize(serializer)
        elif isinstance(self.data, Publish):
            logger.debug(f"Serializing Publish Command: {self.data}")
            serializer.write_u8(CommandKind.Publish)
            self.data.serialize(serializer)
        elif isinstance(self.data, Upgrade):
            logger.debug(f"Serializing Upgrade Command: {self.data}")
            serializer.write_u8(CommandKind.Upgrade)
            self.data.serialize(serializer)
        elif isinstance(self.data, MakeMoveVec):
            logger.debug(f"Serializing MakeMoveVec Command: {self.data}")
            serializer.write_u8(CommandKind.MakeMoveVec)
            self.data.serialize(serializer)
        else:
            raise ValueError(f"Unknown command type: {type(self.data)}")
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes - handles all command types internally."""
        tag = deserializer.read_u8()
        
        if tag == CommandKind.MoveCall:
            data = MoveCall.deserialize(deserializer)
        elif tag == CommandKind.TransferObjects:
            data = TransferObjects.deserialize(deserializer)
        elif tag == CommandKind.SplitCoins:
            data = SplitCoins.deserialize(deserializer)
        elif tag == CommandKind.MergeCoins:
            data = MergeCoins.deserialize(deserializer)
        elif tag == CommandKind.Publish:
            data = Publish.deserialize(deserializer)
        elif tag == CommandKind.Upgrade:
            data = Upgrade.deserialize(deserializer)
        elif tag == CommandKind.MakeMoveVec:
            data = MakeMoveVec.deserialize(deserializer)
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
        transfer = TransferObjects(objects=objects, recipient=recipient)
        return cls(data=transfer)
    
    @classmethod
    def split_coins(cls, coin, amounts: list) -> "Command":
        """Create a SplitCoins command."""
        split = SplitCoins(coin=coin, amounts=amounts)
        return cls(data=split)
    
    @classmethod
    def merge_coins(cls, destination, sources: list) -> "Command":
        """Create a MergeCoins command."""
        merge = MergeCoins(destination=destination, sources=sources)
        return cls(data=merge)
    
    @classmethod
    def publish(cls, modules: list, dependencies: list) -> "Command":
        """Create a Publish command."""
        publish = Publish(modules=modules, dependencies=dependencies)
        return cls(data=publish)
    
    @classmethod
    def upgrade(cls, modules: list, dependencies: list, package: str, ticket) -> "Command":
        """Create an Upgrade command."""
        upgrade = Upgrade(
            modules=modules, 
            dependencies=dependencies,
            package=package,
            ticket=ticket
        )
        return cls(data=upgrade)
    
    @classmethod
    def make_move_vec(cls, type_argument: str = None, elements: list = None) -> "Command":
        """Create a MakeMoveVec command."""
        make_vec = MakeMoveVec(
            type_argument=type_argument,
            elements=elements or []
        )
        return cls(data=make_vec)


# Type alias for backward compatibility
AnyCommand = Command 