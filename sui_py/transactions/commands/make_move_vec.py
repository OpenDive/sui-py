"""
MakeMoveVec pure data structure.

This module defines the MakeMoveVec data structure that can serialize independently,
matching the C# Unity SDK pattern.
"""

from dataclasses import dataclass
from typing import List, Optional
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer, BcsVector, bcs_vector, BcsOption, bcs_some, bcs_none
from ..transaction_argument import TransactionArgument, deserialize_transaction_argument
from ..utils import BcsString


@dataclass
class MakeMoveVec(BcsSerializable):
    """
    Pure MakeMoveVec data structure that can serialize independently.
    
    Creates a vector of objects or values with the same type. This is required
    when constructing vectors in Move, as the type system cannot infer empty vectors.
    
    This corresponds to the C# MakeMoveVec class and contains:
    - type_argument: Optional type parameter for the vector
    - elements: List of elements to include in the vector
    """
    type_argument: Optional[str]               # Optional type parameter
    elements: List[TransactionArgument]        # Elements in the vector
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the MakeMoveVec to BCS bytes.
        
        This matches the C# MakeMoveVec.Serialize method:
        1. Type argument as Option<String>
        2. Elements as vector of TransactionArguments
        """
        # Serialize type argument as option
        if self.type_argument is not None:
            type_option = bcs_some(BcsString(self.type_argument))
        else:
            type_option = bcs_none()
        
        type_option.serialize(serializer)
        
        # Serialize elements vector
        bcs_vector(self.elements).serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a MakeMoveVec from BCS bytes."""
        # Deserialize type argument option
        type_option = BcsOption.deserialize(deserializer, BcsString.deserialize)
        type_argument = type_option.value.value if type_option.value is not None else None
        
        # Deserialize elements
        elements_count = deserializer.read_uleb128()
        elements = []
        for _ in range(elements_count):
            element = deserialize_transaction_argument(deserializer)
            elements.append(element)
        
        return cls(
            type_argument=type_argument,
            elements=elements
        ) 