"""
Complete transaction data structure implementation.
"""

from dataclasses import dataclass
from ...bcs import Serializer, Deserializer, Serializable, serialize
from .base import TransactionType
from .transaction_data_v1 import TransactionDataV1

from ...utils.logging import setup_logging, get_logger
import logging

@dataclass
class TransactionData(Serializable):
    """Complete transaction data structure matching C# implementation."""
    
    setup_logging(level=logging.DEBUG, use_emojis=True)
    logger = get_logger("sui_py.transactions.data.transaction_data")
    
    transaction_type: TransactionType
    transaction_data_v1: TransactionDataV1
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize complete transaction data."""
        # Serialize transaction type (0 for V1)
        serializer.write_u8(self.transaction_type.value)
        
        # Serialize V1 data
        self.transaction_data_v1.serialize(serializer)
        
        self.logger.debug(f"Serialized transaction data: {list(serializer.to_bytes())}")
    
    def to_bytes(self) -> bytes:
        """
        Serialize the transaction data to BCS bytes.
        
        Returns:
            The BCS-encoded transaction data
        """
        return serialize(self)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> 'TransactionData':
        """Deserialize complete transaction data."""
        transaction_type = TransactionType(deserializer.read_u8())
        transaction_data_v1 = TransactionDataV1.deserialize(deserializer)
        
        return cls(
            transaction_type=transaction_type,
            transaction_data_v1=transaction_data_v1
        )
