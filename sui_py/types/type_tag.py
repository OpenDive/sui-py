#!/usr/bin/env python3
"""
Move TypeTag system for serializing type arguments.

This module implements the TypeTag enum and related structures used for 
serializing Move type arguments in a structured format rather than as strings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Union
from abc import ABC, abstractmethod

from ..bcs import BcsSerializable, Serializer, Deserializer
from .base import SuiAddress


class TypeTag(BcsSerializable, ABC):
    """Base class for all Move type tags."""
    
    @abstractmethod
    def get_tag(self) -> int:
        """Get the enum variant tag for this type."""
        pass
    
    @abstractmethod
    def serialize_data(self, serializer: Serializer) -> None:
        """Serialize the type-specific data."""
        pass
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the type tag with variant tag."""
        serializer.write_u8(self.get_tag())
        self.serialize_data(serializer)


@dataclass
class BoolTypeTag(TypeTag):
    """Boolean type tag."""
    
    def get_tag(self) -> int:
        return 0
    
    def serialize_data(self, serializer: Serializer) -> None:
        pass  # No additional data for bool type


@dataclass
class U8TypeTag(TypeTag):
    """U8 type tag."""
    
    def get_tag(self) -> int:
        return 1
    
    def serialize_data(self, serializer: Serializer) -> None:
        pass  # No additional data for u8 type


@dataclass 
class U64TypeTag(TypeTag):
    """U64 type tag."""
    
    def get_tag(self) -> int:
        return 2
    
    def serialize_data(self, serializer: Serializer) -> None:
        pass  # No additional data for u64 type


@dataclass
class U128TypeTag(TypeTag):
    """U128 type tag."""
    
    def get_tag(self) -> int:
        return 3
    
    def serialize_data(self, serializer: Serializer) -> None:
        pass  # No additional data for u128 type


@dataclass
class AddressTypeTag(TypeTag):
    """Address type tag."""
    
    def get_tag(self) -> int:
        return 4
    
    def serialize_data(self, serializer: Serializer) -> None:
        pass  # No additional data for address type


@dataclass
class SignerTypeTag(TypeTag):
    """Signer type tag."""
    
    def get_tag(self) -> int:
        return 5
    
    def serialize_data(self, serializer: Serializer) -> None:
        pass  # No additional data for signer type


@dataclass
class VectorTypeTag(TypeTag):
    """Vector type tag."""
    element_type: TypeTag
    
    def get_tag(self) -> int:
        return 6
    
    def serialize_data(self, serializer: Serializer) -> None:
        self.element_type.serialize(serializer)


@dataclass
class StructTypeTag(TypeTag):
    """Struct type tag with address, module, name, and type parameters."""
    address: SuiAddress
    module: str  
    name: str
    type_params: List[TypeTag]
    
    def get_tag(self) -> int:
        return 7
    
    def serialize_data(self, serializer: Serializer) -> None:
        from sui_py.transactions.utils import BcsString
        from sui_py.bcs import bcs_vector
        
        # Serialize address (32 bytes)
        self.address.serialize(serializer)
        
        # Serialize module name
        BcsString(self.module).serialize(serializer)
        
        # Serialize struct name  
        BcsString(self.name).serialize(serializer)
        
        # Serialize type parameters
        type_params_vector = bcs_vector(self.type_params)
        type_params_vector.serialize(serializer)


@dataclass
class U16TypeTag(TypeTag):
    """U16 type tag."""
    
    def get_tag(self) -> int:
        return 8
    
    def serialize_data(self, serializer: Serializer) -> None:
        pass  # No additional data for u16 type


@dataclass
class U32TypeTag(TypeTag):
    """U32 type tag."""
    
    def get_tag(self) -> int:
        return 9
    
    def serialize_data(self, serializer: Serializer) -> None:
        pass  # No additional data for u32 type


@dataclass
class U256TypeTag(TypeTag):
    """U256 type tag."""
    
    def get_tag(self) -> int:
        return 10
    
    def serialize_data(self, serializer: Serializer) -> None:
        pass  # No additional data for u256 type


def parse_type_tag(type_str: str) -> TypeTag:
    """
    Parse a type string into a TypeTag.
    
    Args:
        type_str: Type string like "bool", "u64", "0x2::coin::Coin", etc.
        
    Returns:
        Corresponding TypeTag instance
    """
    type_str = type_str.strip()
    
    # Simple types
    if type_str == "bool":
        return BoolTypeTag()
    elif type_str == "u8":
        return U8TypeTag()
    elif type_str == "u16":
        return U16TypeTag() 
    elif type_str == "u32":
        return U32TypeTag()
    elif type_str == "u64":
        return U64TypeTag()
    elif type_str == "u128":
        return U128TypeTag()
    elif type_str == "u256":
        return U256TypeTag()
    elif type_str == "address":
        return AddressTypeTag()
    elif type_str == "signer":
        return SignerTypeTag()
    
    # Vector types
    if type_str.startswith("vector<") and type_str.endswith(">"):
        inner_type = type_str[7:-1]  # Remove "vector<" and ">"
        element_type = parse_type_tag(inner_type)
        return VectorTypeTag(element_type)
    
    # Struct types - pattern: address::module::name or address::module::name<type1, type2>
    if "::" in type_str:
        # Handle generic types
        if "<" in type_str and type_str.endswith(">"):
            # Extract base type and type parameters
            base_end = type_str.index("<")
            base_type = type_str[:base_end]
            type_params_str = type_str[base_end+1:-1]
            
            # Parse type parameters
            type_params = []
            if type_params_str.strip():
                # Simple split by comma (doesn't handle nested generics properly)
                param_strs = [p.strip() for p in type_params_str.split(",")]
                type_params = [parse_type_tag(p) for p in param_strs]
            
            parts = base_type.split("::")
        else:
            parts = type_str.split("::")
            type_params = []
        
        if len(parts) == 3:
            address_str, module, name = parts
            address = SuiAddress(address_str)
            return StructTypeTag(address, module, name, type_params)
    
    raise ValueError(f"Unable to parse type string: {type_str}")


def deserialize_type_tag(deserializer: Deserializer) -> TypeTag:
    """Deserialize a TypeTag from bytes."""
    tag = deserializer.read_u8()
    
    if tag == 0:
        return BoolTypeTag()
    elif tag == 1:
        return U8TypeTag()
    elif tag == 2:
        return U64TypeTag()
    elif tag == 3:
        return U128TypeTag()
    elif tag == 4:
        return AddressTypeTag()
    elif tag == 5:
        return SignerTypeTag()
    elif tag == 6:
        element_type = deserialize_type_tag(deserializer)
        return VectorTypeTag(element_type)
    elif tag == 7:
        from sui_py.transactions.utils import BcsString
        from sui_py.bcs import BcsVector
        
        address = SuiAddress.deserialize(deserializer)
        module = BcsString.deserialize(deserializer).value
        name = BcsString.deserialize(deserializer).value
        type_params_vector = BcsVector.deserialize(deserializer, deserialize_type_tag)
        type_params = type_params_vector.elements
        
        return StructTypeTag(address, module, name, type_params)
    elif tag == 8:
        return U16TypeTag()
    elif tag == 9:
        return U32TypeTag()
    elif tag == 10:
        return U256TypeTag()
    else:
        raise ValueError(f"Unknown TypeTag variant: {tag}") 