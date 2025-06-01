"""
MergeCoins pure data structure.

This module defines the MergeCoins data structure that can serialize independently,
matching the C# Unity SDK pattern.
"""

from dataclasses import dataclass
from typing import List
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer, BcsVector, bcs_vector
from ..transaction_argument import TransactionArgument, deserialize_transaction_argument


@dataclass
class MergeCoins(BcsSerializable):
    """
    Pure MergeCoins data structure that can serialize independently.
    
    Merges multiple coins of the same type into a destination coin.
    The source coins are destroyed and their balances added to the destination.
    
    This corresponds to the C# MergeCoins class and contains:
    - destination: The destination coin to merge into
    - sources: List of source coins to merge
    """
    destination: TransactionArgument    # Destination coin
    sources: List[TransactionArgument]  # Source coins to merge
    
    def __post_init__(self):
        """Validate merge parameters."""
        if not self.sources:
            raise ValueError("Must specify at least one source coin to merge")
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the MergeCoins to BCS bytes.
        
        This matches the C# MergeCoins.Serialize method:
        1. Destination as TransactionArgument
        2. Sources as vector of TransactionArguments
        """
        # Serialize destination
        self.destination.serialize(serializer)
        
        # Serialize sources vector
        bcs_vector(self.sources).serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a MergeCoins from BCS bytes."""
        # Deserialize destination
        destination = deserialize_transaction_argument(deserializer)
        
        # Deserialize sources
        sources_count = deserializer.read_uleb128()
        sources = []
        for _ in range(sources_count):
            source = deserialize_transaction_argument(deserializer)
            sources.append(source)
        
        return cls(
            destination=destination,
            sources=sources
        ) 