"""
Transaction expiration data structure.

The TransactionExpiration type represents when a transaction should expire.
It has two variants:
- None: The transaction has no expiration
- Epoch(u64): The transaction expires at the specified epoch
"""

from dataclasses import dataclass
from typing import Optional
from ...bcs import Serializer, Deserializer, Serializable

@dataclass
class TransactionExpiration(Serializable):
    """
    Transaction expiration data.
    
    Attributes:
        epoch: Optional[int] - If set, the epoch at which the transaction expires.
               If None, the transaction has no expiration.
    """
    epoch: Optional[int] = None
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize transaction expiration."""
        if self.epoch is None:
            serializer.write_u8(0)  # None variant
        else:
            serializer.write_u8(1)  # Epoch variant
            serializer.write_u64(self.epoch)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> 'TransactionExpiration':
        """Deserialize transaction expiration."""
        tag = deserializer.read_u8()
        if tag == 0:  # None variant
            return cls()
        elif tag == 1:  # Epoch variant
            epoch = deserializer.read_u64()
            return cls(epoch=epoch)
        else:
            raise ValueError(f"Invalid TransactionExpiration tag: {tag}")
