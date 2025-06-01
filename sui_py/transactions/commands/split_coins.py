"""
SplitCoins pure data structure.

This module defines the SplitCoins data structure that can serialize independently,
matching the C# Unity SDK pattern.
"""

from dataclasses import dataclass
from typing import List
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer, BcsVector, bcs_vector
from ..arguments import TransactionArgument, deserialize_transaction_argument


@dataclass
class SplitCoins(BcsSerializable):
    """
    Pure SplitCoins data structure that can serialize independently.
    
    Splits a coin into multiple new coins with specified amounts.
    The original coin's balance is reduced by the total split amount.
    
    This corresponds to the C# SplitCoins class and contains:
    - coin: The coin to split
    - amounts: List of amounts for the new coins
    """
    coin: TransactionArgument           # Coin to split
    amounts: List[TransactionArgument]  # Amounts for new coins
    
    def __post_init__(self):
        """Validate split parameters."""
        if not self.amounts:
            raise ValueError("Must specify at least one amount to split")
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the SplitCoins to BCS bytes.
        
        This matches the C# SplitCoins.Serialize method:
        1. Coin as TransactionArgument
        2. Amounts as vector of TransactionArguments
        """
        # Serialize coin
        self.coin.serialize(serializer)
        
        # Serialize amounts vector
        bcs_vector(self.amounts).serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a SplitCoins from BCS bytes."""
        # Deserialize coin
        coin = deserialize_transaction_argument(deserializer)
        
        # Deserialize amounts
        amounts_count = deserializer.read_uleb128()
        amounts = []
        for _ in range(amounts_count):
            amount = deserialize_transaction_argument(deserializer)
            amounts.append(amount)
        
        return cls(
            coin=coin,
            amounts=amounts
        ) 