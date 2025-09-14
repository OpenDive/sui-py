"""
Move Utils API types for SuiPy SDK.

This module defines data structures for Move Utils API requests and responses,
including normalized representations of Move functions, modules, and structs.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SuiMoveFunctionArgType:
    """Move function argument type information."""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuiMoveFunctionArgType":
        """Create a SuiMoveFunctionArgType from API response data."""
        return cls()


@dataclass
class SuiMoveNormalizedFunction:
    """Normalized representation of a Move function."""
    visibility: str
    is_entry: bool
    type_parameters: List[Dict[str, Any]]
    parameters: List[str]
    return_: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuiMoveNormalizedFunction":
        """Create a SuiMoveNormalizedFunction from API response data."""
        return cls(
            visibility=data.get("visibility", ""),
            is_entry=data.get("isEntry", False),
            type_parameters=data.get("typeParameters", []),
            parameters=data.get("parameters", []),
            return_=data.get("return", [])
        )


@dataclass
class SuiMoveNormalizedStruct:
    """Normalized representation of a Move struct."""
    abilities: Dict[str, bool]
    type_parameters: List[Dict[str, Any]]
    fields: List[Dict[str, Any]]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuiMoveNormalizedStruct":
        """Create a SuiMoveNormalizedStruct from API response data."""
        return cls(
            abilities=data.get("abilities", {}),
            type_parameters=data.get("typeParameters", []),
            fields=data.get("fields", [])
        )


@dataclass
class SuiMoveNormalizedModule:
    """Normalized representation of a Move module."""
    file_format_version: int
    address: str
    name: str
    friends: List[Dict[str, str]]
    structs: Dict[str, SuiMoveNormalizedStruct]
    exposed_functions: Dict[str, SuiMoveNormalizedFunction]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuiMoveNormalizedModule":
        """Create a SuiMoveNormalizedModule from API response data."""
        # Parse structs
        structs = {}
        for name, struct_data in data.get("structs", {}).items():
            structs[name] = SuiMoveNormalizedStruct.from_dict(struct_data)
        
        # Parse exposed functions
        exposed_functions = {}
        for name, func_data in data.get("exposedFunctions", {}).items():
            exposed_functions[name] = SuiMoveNormalizedFunction.from_dict(func_data)
        
        return cls(
            file_format_version=data.get("fileFormatVersion", 0),
            address=data.get("address", ""),
            name=data.get("name", ""),
            friends=data.get("friends", []),
            structs=structs,
            exposed_functions=exposed_functions
        )
