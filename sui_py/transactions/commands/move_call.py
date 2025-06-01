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
from ..transaction_argument import TransactionArgument, deserialize_transaction_argument
from ..utils import BcsString, parse_move_call_target, validate_object_id


@dataclass
class MoveCall(BcsSerializable):
    """
    Pure MoveCall data structure that can serialize independently.
    
    This corresponds to the C# MoveCall class and contains:
    - package: The package ID
    - module: The module name
    - function: The function name  
    - type_arguments: List of type arguments
    - arguments: List of TransactionArguments
    """
    package: str  # Package ID
    module: str   # Module name
    function: str # Function name
    type_arguments: List[str]  # Type argument strings
    arguments: List[TransactionArgument]  # Transaction arguments
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the MoveCall to BCS bytes.
        
        This matches the C# MoveCall.Serialize method exactly:
        1. Package ID as ObjectID 
        2. Module name as string
        3. Function name as string
        4. Type arguments as vector of TypeTags
        5. Arguments as vector of TransactionArguments
        """
        # Serialize package ID (32 bytes without length prefix)
        validate_object_id(self.package)
        serializer.write_bytes(bytes.fromhex(self.package[2:]))  # Remove 0x prefix
        
        # Serialize module name
        BcsString(self.module).serialize(serializer)
        
        # Serialize function name  
        BcsString(self.function).serialize(serializer)
        
        # Serialize type arguments
        type_tags = [parse_type_tag(type_arg) for type_arg in self.type_arguments]
        bcs_vector(type_tags).serialize(serializer)
        
        # Serialize arguments
        bcs_vector(self.arguments).serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a MoveCall from BCS bytes."""
        # Deserialize package ID (32 bytes)
        package_bytes = deserializer.read_bytes(32)
        package = "0x" + package_bytes.hex()
        
        # Deserialize module name
        module = BcsString.deserialize(deserializer).value
        
        # Deserialize function name
        function = BcsString.deserialize(deserializer).value
        
        # Deserialize type arguments
        type_tag_count = deserializer.read_uleb128()
        type_arguments = []
        for _ in range(type_tag_count):
            type_tag = deserialize_type_tag(deserializer)
            type_arguments.append(str(type_tag))
        
        # Deserialize arguments
        arg_count = deserializer.read_uleb128()
        arguments = []
        for _ in range(arg_count):
            arg = deserialize_transaction_argument(deserializer)
            arguments.append(arg)
        
        return cls(
            package=package,
            module=module,
            function=function,
            type_arguments=type_arguments,
            arguments=arguments
        )
    
    @classmethod
    def from_target(cls, target: str, arguments: List[TransactionArgument] = None, type_arguments: List[str] = None) -> "MoveCall":
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