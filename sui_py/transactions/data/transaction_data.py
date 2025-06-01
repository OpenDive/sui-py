"""
Complete transaction data structure implementation.
"""

from dataclasses import dataclass
from ...bcs import Serializer, Deserializer, Serializable
from .base import TransactionType
from .transaction_data_v1 import TransactionDataV1

@dataclass
class TransactionData(Serializable):
    """Complete transaction data structure matching C# implementation."""
    
    transaction_type: TransactionType
    transaction_data_v1: TransactionDataV1
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize complete transaction data."""
        # Serialize transaction type (0 for V1)
        serializer.write_u8(self.transaction_type.value)
        
        # Serialize V1 data
        self.transaction_data_v1.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> 'TransactionData':
        """Deserialize complete transaction data."""
        transaction_type = TransactionType(deserializer.read_u8())
        transaction_data_v1 = TransactionDataV1.deserialize(deserializer)
        
        return cls(
            transaction_type=transaction_type,
            transaction_data_v1=transaction_data_v1
        )
