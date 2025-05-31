"""
MoveCall pure data structure.

This module defines the MoveCall data structure that can serialize independently,
matching the C# Unity SDK MoveCall.cs implementation.
"""

from dataclasses import dataclass
from typing import List
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer, BcsVector, bcs_vector
from ...types import ObjectID
from ...types.type_tag import parse_type_tag, deserialize_type_tag
from ..arguments import CommandArgument, deserialize_command_argument
from ..utils import BcsString, parse_move_call_target, validate_object_id


@dataclass
class MoveCall(BcsSerializable):
    """
    Pure MoveCall data structure that can serialize independently.
    
    This corresponds to the C# MoveCall class that implements ICommand.
    When serialized directly, it produces just the MoveCall data without
    any command envelope tags.
    
    A Move Call executes any public Move function with the provided arguments
    and type parameters. This is the primary way to interact with smart contracts.
    """
    package: str
    module: str
    function: str
    type_arguments: List[str]
    arguments: List[CommandArgument]
    
    def __post_init__(self):
        """Validate Move call parameters."""
        self.package = validate_object_id(self.package)
        if not self.module:
            raise ValueError("Module name cannot be empty")
        if not self.function:
            raise ValueError("Function name cannot be empty")
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize MoveCall data directly (no command tag).
        
        This matches the C# MoveCall.Serialize() behavior and produces
        the exact bytes expected by the BCS test.
        
        Format:
        1. Package ID (32 bytes)
        2. Module name (string with length prefix)
        3. Function name (string with length prefix)  
        4. Type arguments (vector of TypeTag)
        5. Arguments (vector of CommandArgument)
        """
        # Serialize package ID
        ObjectID(self.package).serialize(serializer)
        
        # Serialize module and function names
        BcsString(self.module).serialize(serializer)
        BcsString(self.function).serialize(serializer)
        
        # Serialize type arguments using TypeTag system
        type_tags = [parse_type_tag(arg) for arg in self.type_arguments]
        type_args_vector = bcs_vector(type_tags)
        type_args_vector.serialize(serializer)
        
        # Serialize arguments
        args_vector = bcs_vector(self.arguments)
        args_vector.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize MoveCall data (no command tag expected)."""
        package = ObjectID.deserialize(deserializer).value
        module = BcsString.deserialize(deserializer).value
        function = BcsString.deserialize(deserializer).value
        
        # Read type arguments using TypeTag system
        type_args_vector = BcsVector.deserialize(deserializer, deserialize_type_tag)
        # Convert TypeTag objects back to strings for now
        type_arguments = [str(tag) for tag in type_args_vector.elements]
        
        # Read arguments
        args_vector = BcsVector.deserialize(deserializer, deserialize_command_argument)
        arguments = args_vector.elements
        
        return cls(package, module, function, type_arguments, arguments)
    
    @classmethod
    def from_target(cls, target: str, arguments: List[CommandArgument] = None, type_arguments: List[str] = None) -> "MoveCall":
        """
        Create a MoveCall from a target string.
        
        Args:
            target: Target in format "package::module::function"
            arguments: Function arguments
            type_arguments: Type parameters
            
        Returns:
            A new MoveCall data structure
        """
        package, module, function = parse_move_call_target(target)
        return cls(
            package=package,
            module=module,
            function=function,
            type_arguments=type_arguments or [],
            arguments=arguments or []
        ) 