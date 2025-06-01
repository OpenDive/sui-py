"""
TransferObjects pure data structure.

This module defines the TransferObjects data structure that can serialize independently,
matching the C# Unity SDK pattern.
"""

from dataclasses import dataclass
from typing import List
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer, BcsVector, bcs_vector
from ..transaction_argument import TransactionArgument, deserialize_transaction_argument


@dataclass
class TransferObjects(BcsSerializable):
    """
    Pure TransferObjects data structure that can serialize independently.
    
    Transfers a list of objects to a recipient address. Objects must have
    the 'store' ability and be owned by the transaction sender.
    
    This corresponds to the C# TransferObjects class and contains:
    - objects: List of objects to transfer
    - recipient: Address to transfer objects to
    """
    objects: List[TransactionArgument]  # Objects to transfer
    recipient: TransactionArgument      # Recipient address
    
    def __post_init__(self):
        """Validate transfer parameters."""
        if not self.objects:
            raise ValueError("Must specify at least one object to transfer")
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the TransferObjects to BCS bytes.
        
        This matches the C# TransferObjects.Serialize method:
        1. Objects as vector of TransactionArguments
        2. Recipient as TransactionArgument
        """
        # Serialize objects vector
        bcs_vector(self.objects).serialize(serializer)
        
        # Serialize recipient
        self.recipient.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a TransferObjects from BCS bytes."""
        # Deserialize objects
        objects_count = deserializer.read_uleb128()
        objects = []
        for _ in range(objects_count):
            obj = deserialize_transaction_argument(deserializer)
            objects.append(obj)
        
        # Deserialize recipient
        recipient = deserialize_transaction_argument(deserializer)
        
        return cls(
            objects=objects,
            recipient=recipient
        ) 