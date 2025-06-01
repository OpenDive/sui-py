"""
Publish pure data structure.

This module defines the Publish data structure that can serialize independently,
matching the C# Unity SDK pattern.
"""

from dataclasses import dataclass
from typing import List
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer, BcsVector, bcs_vector, U8
from ...types import ObjectID
from ..utils import validate_object_id


@dataclass
class Publish(BcsSerializable):
    """
    Pure Publish data structure that can serialize independently.
    
    Publishes a new Move package to the blockchain. The package must be
    compiled to bytecode and all dependencies must be available on-chain.
    
    This corresponds to the C# Publish class and contains:
    - modules: List of compiled Move module bytecode
    - dependencies: List of package IDs this package depends on
    """
    modules: List[bytes]  # Compiled Move module bytecode
    dependencies: List[str]  # Package IDs of dependencies
    
    def __post_init__(self):
        """Validate publish parameters."""
        if not self.modules:
            raise ValueError("Must specify at least one module to publish")
        
        # Validate dependency object IDs
        self.dependencies = [validate_object_id(dep) for dep in self.dependencies]
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the Publish to BCS bytes.
        
        This matches the C# Publish.Serialize method:
        1. Modules as vector of byte vectors
        2. Dependencies as vector of ObjectIDs
        """
        # Serialize modules as vector of byte vectors
        modules_data = []
        for module in self.modules:
            module_vector = bcs_vector([U8(b) for b in module])
            modules_data.append(module_vector)
        
        modules_vector = bcs_vector(modules_data)
        modules_vector.serialize(serializer)
        
        # Serialize dependencies as vector of ObjectIDs
        deps_vector = bcs_vector([ObjectID(dep) for dep in self.dependencies])
        deps_vector.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a Publish from BCS bytes."""
        # Deserialize modules
        modules_count = deserializer.read_uleb128()
        modules = []
        for _ in range(modules_count):
            # Read module as vector of U8
            module_length = deserializer.read_uleb128()
            module_bytes = []
            for _ in range(module_length):
                byte_val = U8.deserialize(deserializer)
                module_bytes.append(byte_val.value)
            modules.append(bytes(module_bytes))
        
        # Deserialize dependencies
        deps_count = deserializer.read_uleb128()
        dependencies = []
        for _ in range(deps_count):
            dep = ObjectID.deserialize(deserializer)
            dependencies.append(dep.value)
        
        return cls(
            modules=modules,
            dependencies=dependencies
        ) 