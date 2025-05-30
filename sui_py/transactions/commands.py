"""
Transaction command types for Programmable Transaction Blocks.

This module defines all command types that can be executed in a PTB,
including Move calls, object transfers, coin operations, and package management.
All commands implement the BCS protocol for proper serialization.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Union, Optional
from typing_extensions import Self

from ..bcs import BcsSerializable, Serializer, Deserializer, BcsVector, bcs_vector
from ..types import ObjectID
from .arguments import AnyArgument, deserialize_argument
from .utils import BcsString, parse_move_call_target, validate_object_id


class TransactionCommand(BcsSerializable, ABC):
    """Base class for all transaction commands."""
    
    @abstractmethod
    def get_command_tag(self) -> int:
        """Get the BCS enum variant tag for this command type."""
        pass
    
    @abstractmethod
    def serialize_command_data(self, serializer: Serializer) -> None:
        """Serialize the command-specific data."""
        pass
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize with proper BCS enum format."""
        serializer.write_u8(self.get_command_tag())
        self.serialize_command_data(serializer)


@dataclass
class MoveCallCommand(TransactionCommand):
    """
    Move function call command.
    
    Executes a public or entry Move function with the provided arguments
    and type parameters. This is the primary way to interact with smart contracts.
    """
    package: str
    module: str
    function: str
    type_arguments: List[str]
    arguments: List[AnyArgument]
    
    def __post_init__(self):
        """Validate Move call parameters."""
        self.package = validate_object_id(self.package)
        if not self.module:
            raise ValueError("Module name cannot be empty")
        if not self.function:
            raise ValueError("Function name cannot be empty")
    
    def get_command_tag(self) -> int:
        return 0  # MoveCall variant
    
    def serialize_command_data(self, serializer: Serializer) -> None:
        """Serialize Move call data."""
        # Serialize package ID
        ObjectID(self.package).serialize(serializer)
        
        # Serialize module and function names
        BcsString(self.module).serialize(serializer)
        BcsString(self.function).serialize(serializer)
        
        # Serialize type arguments
        type_args_vector = bcs_vector([BcsString(arg) for arg in self.type_arguments])
        type_args_vector.serialize(serializer)
        
        # Serialize arguments
        args_vector = bcs_vector(self.arguments)
        args_vector.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a Move call command."""
        package = ObjectID.deserialize(deserializer).value
        module = BcsString.deserialize(deserializer).value
        function = BcsString.deserialize(deserializer).value
        
        # Read type arguments
        type_args_vector = BcsVector.deserialize(deserializer, BcsString.deserialize)
        type_arguments = [arg.value for arg in type_args_vector.elements]
        
        # Read arguments
        args_vector = BcsVector.deserialize(deserializer, deserialize_argument)
        arguments = args_vector.elements
        
        return cls(package, module, function, type_arguments, arguments)
    
    @classmethod
    def from_target(cls, target: str, arguments: List[AnyArgument] = None, type_arguments: List[str] = None) -> "MoveCallCommand":
        """
        Create a Move call command from a target string.
        
        Args:
            target: Target in format "package::module::function"
            arguments: Function arguments
            type_arguments: Type parameters
            
        Returns:
            A new MoveCallCommand
        """
        package, module, function = parse_move_call_target(target)
        return cls(
            package=package,
            module=module,
            function=function,
            type_arguments=type_arguments or [],
            arguments=arguments or []
        )


@dataclass
class TransferObjectsCommand(TransactionCommand):
    """
    Transfer objects command.
    
    Transfers a list of objects to a recipient address. Objects must have
    the 'store' ability and be owned by the transaction sender.
    """
    objects: List[AnyArgument]
    recipient: AnyArgument
    
    def __post_init__(self):
        """Validate transfer parameters."""
        if not self.objects:
            raise ValueError("Must specify at least one object to transfer")
    
    def get_command_tag(self) -> int:
        return 1  # TransferObjects variant
    
    def serialize_command_data(self, serializer: Serializer) -> None:
        """Serialize transfer data."""
        objects_vector = bcs_vector(self.objects)
        objects_vector.serialize(serializer)
        self.recipient.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a transfer objects command."""
        objects_vector = BcsVector.deserialize(deserializer, deserialize_argument)
        objects = objects_vector.elements
        recipient = deserialize_argument(deserializer)
        return cls(objects, recipient)


@dataclass
class SplitCoinsCommand(TransactionCommand):
    """
    Split coins command.
    
    Splits a coin into multiple new coins with specified amounts.
    The original coin's balance is reduced by the total split amount.
    """
    coin: AnyArgument
    amounts: List[AnyArgument]
    
    def __post_init__(self):
        """Validate split parameters."""
        if not self.amounts:
            raise ValueError("Must specify at least one amount to split")
    
    def get_command_tag(self) -> int:
        return 2  # SplitCoins variant
    
    def serialize_command_data(self, serializer: Serializer) -> None:
        """Serialize split data."""
        self.coin.serialize(serializer)
        amounts_vector = bcs_vector(self.amounts)
        amounts_vector.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a split coins command."""
        coin = deserialize_argument(deserializer)
        amounts_vector = BcsVector.deserialize(deserializer, deserialize_argument)
        amounts = amounts_vector.elements
        return cls(coin, amounts)


@dataclass
class MergeCoinsCommand(TransactionCommand):
    """
    Merge coins command.
    
    Merges multiple coins of the same type into a destination coin.
    The source coins are destroyed and their balances added to the destination.
    """
    destination: AnyArgument
    sources: List[AnyArgument]
    
    def __post_init__(self):
        """Validate merge parameters."""
        if not self.sources:
            raise ValueError("Must specify at least one source coin to merge")
    
    def get_command_tag(self) -> int:
        return 3  # MergeCoins variant
    
    def serialize_command_data(self, serializer: Serializer) -> None:
        """Serialize merge data."""
        self.destination.serialize(serializer)
        sources_vector = bcs_vector(self.sources)
        sources_vector.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a merge coins command."""
        destination = deserialize_argument(deserializer)
        sources_vector = BcsVector.deserialize(deserializer, deserialize_argument)
        sources = sources_vector.elements
        return cls(destination, sources)


@dataclass
class PublishCommand(TransactionCommand):
    """
    Package publish command.
    
    Publishes a new Move package to the blockchain. The package must be
    compiled to bytecode and all dependencies must be available on-chain.
    """
    modules: List[bytes]
    dependencies: List[str]
    
    def __post_init__(self):
        """Validate publish parameters."""
        if not self.modules:
            raise ValueError("Must specify at least one module to publish")
        
        # Validate dependency object IDs
        self.dependencies = [validate_object_id(dep) for dep in self.dependencies]
    
    def get_command_tag(self) -> int:
        return 4  # Publish variant
    
    def serialize_command_data(self, serializer: Serializer) -> None:
        """Serialize publish data."""
        from ..bcs import U8
        
        # Serialize modules as vector of byte vectors
        modules_data = []
        for module in self.modules:
            module_vector = bcs_vector([U8(b) for b in module])
            modules_data.append(module_vector)
        
        modules_vector = bcs_vector(modules_data)
        modules_vector.serialize(serializer)
        
        # Serialize dependencies
        deps_vector = bcs_vector([ObjectID(dep) for dep in self.dependencies])
        deps_vector.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a publish command."""
        from ..bcs import U8
        
        # Read modules
        modules_vector = BcsVector.deserialize(
            deserializer, 
            lambda d: BcsVector.deserialize(d, U8.deserialize)
        )
        modules = [bytes([u8.value for u8 in module.elements]) for module in modules_vector.elements]
        
        # Read dependencies
        deps_vector = BcsVector.deserialize(deserializer, ObjectID.deserialize)
        dependencies = [dep.value for dep in deps_vector.elements]
        
        return cls(modules, dependencies)


@dataclass
class UpgradeCommand(TransactionCommand):
    """
    Package upgrade command.
    
    Upgrades an existing Move package with new bytecode. Requires an
    upgrade capability and authorization ticket.
    """
    modules: List[bytes]
    dependencies: List[str]
    package: str
    ticket: AnyArgument
    
    def __post_init__(self):
        """Validate upgrade parameters."""
        if not self.modules:
            raise ValueError("Must specify at least one module to upgrade")
        
        # Validate object IDs
        self.package = validate_object_id(self.package)
        self.dependencies = [validate_object_id(dep) for dep in self.dependencies]
    
    def get_command_tag(self) -> int:
        return 5  # Upgrade variant
    
    def serialize_command_data(self, serializer: Serializer) -> None:
        """Serialize upgrade data."""
        from ..bcs import U8
        
        # Serialize modules as vector of byte vectors
        modules_data = []
        for module in self.modules:
            module_vector = bcs_vector([U8(b) for b in module])
            modules_data.append(module_vector)
        
        modules_vector = bcs_vector(modules_data)
        modules_vector.serialize(serializer)
        
        # Serialize dependencies
        deps_vector = bcs_vector([ObjectID(dep) for dep in self.dependencies])
        deps_vector.serialize(serializer)
        
        # Serialize package ID and ticket
        ObjectID(self.package).serialize(serializer)
        self.ticket.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize an upgrade command."""
        from ..bcs import U8
        
        # Read modules
        modules_vector = BcsVector.deserialize(
            deserializer,
            lambda d: BcsVector.deserialize(d, U8.deserialize)
        )
        modules = [bytes([u8.value for u8 in module.elements]) for module in modules_vector.elements]
        
        # Read dependencies
        deps_vector = BcsVector.deserialize(deserializer, ObjectID.deserialize)
        dependencies = [dep.value for dep in deps_vector.elements]
        
        # Read package and ticket
        package = ObjectID.deserialize(deserializer).value
        ticket = deserialize_argument(deserializer)
        
        return cls(modules, dependencies, package, ticket)


@dataclass
class MakeMoveVecCommand(TransactionCommand):
    """
    Make Move vector command.
    
    Creates a vector of objects or values with the same type. This is required
    when constructing vectors in Move, as the type system cannot infer empty vectors.
    """
    type_argument: Optional[str]
    elements: List[AnyArgument]
    
    def get_command_tag(self) -> int:
        return 6  # MakeMoveVec variant
    
    def serialize_command_data(self, serializer: Serializer) -> None:
        """Serialize make vector data."""
        from ..bcs import BcsOption, bcs_some, bcs_none
        
        # Serialize type argument as option
        if self.type_argument is not None:
            type_option = bcs_some(BcsString(self.type_argument))
        else:
            type_option = bcs_none()
        
        type_option.serialize(serializer)
        
        # Serialize elements
        elements_vector = bcs_vector(self.elements)
        elements_vector.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a make vector command."""
        from ..bcs import BcsOption
        
        # Read type argument option
        type_option = BcsOption.deserialize(deserializer, BcsString.deserialize)
        type_argument = type_option.value.value if type_option.value is not None else None
        
        # Read elements
        elements_vector = BcsVector.deserialize(deserializer, deserialize_argument)
        elements = elements_vector.elements
        
        return cls(type_argument, elements)


# Type alias for all command types
AnyCommand = Union[
    MoveCallCommand,
    TransferObjectsCommand,
    SplitCoinsCommand,
    MergeCoinsCommand,
    PublishCommand,
    UpgradeCommand,
    MakeMoveVecCommand
]


def deserialize_command(deserializer: Deserializer) -> AnyCommand:
    """
    Deserialize any transaction command based on its tag.
    
    Args:
        deserializer: The BCS deserializer
        
    Returns:
        The deserialized command
        
    Raises:
        ValueError: If the command tag is unknown
    """
    tag = deserializer.read_u8()
    
    if tag == 0:
        return MoveCallCommand.deserialize(deserializer)
    elif tag == 1:
        return TransferObjectsCommand.deserialize(deserializer)
    elif tag == 2:
        return SplitCoinsCommand.deserialize(deserializer)
    elif tag == 3:
        return MergeCoinsCommand.deserialize(deserializer)
    elif tag == 4:
        return PublishCommand.deserialize(deserializer)
    elif tag == 5:
        return UpgradeCommand.deserialize(deserializer)
    elif tag == 6:
        return MakeMoveVecCommand.deserialize(deserializer)
    else:
        raise ValueError(f"Unknown command tag: {tag}") 