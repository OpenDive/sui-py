"""
Upgrade pure data structure.

This module defines the Upgrade data structure that can serialize independently,
matching the C# Unity SDK pattern.
"""

from dataclasses import dataclass
from typing import List
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer, BcsVector, bcs_vector, U8
from ...types import ObjectID
from ..transaction_argument import TransactionArgument, deserialize_transaction_argument
from ..utils import validate_object_id


@dataclass
class Upgrade(BcsSerializable):
    """
    Pure Upgrade data structure that can serialize independently.
    
    Upgrades an existing Move package with new bytecode. Requires an
    upgrade capability and authorization ticket.
    
    This corresponds to the C# Upgrade class and contains:
    - modules: List of new compiled Move module bytecode
    - dependencies: List of package IDs this package depends on
    - package: The package ID being upgraded
    - ticket: The upgrade capability ticket
    """
    modules: List[bytes]        # New compiled Move module bytecode
    dependencies: List[str]     # Package IDs of dependencies
    package: str               # Package ID being upgraded
    ticket: TransactionArgument # Upgrade capability ticket
    
    def __post_init__(self):
        """Validate upgrade parameters."""
        if not self.modules:
            raise ValueError("Must specify at least one module to upgrade")
        
        # Validate object IDs
        self.package = validate_object_id(self.package)
        self.dependencies = [validate_object_id(dep) for dep in self.dependencies]
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the Upgrade to BCS bytes.
        
        This matches the C# Upgrade.Serialize method:
        1. Modules as vector of byte vectors
        2. Dependencies as vector of ObjectIDs
        3. Package ID as ObjectID
        4. Ticket as TransactionArgument
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
        
        # Serialize package ID
        ObjectID(self.package).serialize(serializer)
        
        # Serialize ticket
        self.ticket.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize an Upgrade from BCS bytes."""
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
        
        # Deserialize package ID
        package = ObjectID.deserialize(deserializer).value
        
        # Deserialize ticket
        ticket = deserialize_transaction_argument(deserializer)
        
        return cls(
            modules=modules,
            dependencies=dependencies,
            package=package,
            ticket=ticket
        ) 