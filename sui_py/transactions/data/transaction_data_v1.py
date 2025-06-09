"""
Transaction data V1 structure implementation.
"""

from dataclasses import dataclass
from ...bcs import Serializer, Deserializer, Serializable
from ...types import SuiAddress
from .transaction_kind import TransactionKind
from .gas_data import GasData
from .transaction_expiration import TransactionExpiration


from ...utils.logging import setup_logging, get_logger
import logging

@dataclass
class TransactionDataV1(Serializable):
    """Transaction data V1 structure."""
    
    setup_logging(level=logging.DEBUG, use_emojis=True)
    logger = get_logger("sui_py.transactions.data.transaction_data_v1")
    
    transaction_kind: TransactionKind
    sender: SuiAddress
    gas_data: GasData
    expiration: TransactionExpiration  
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize transaction data V1."""
        # Match TypeScript BCS exact order: kind, sender, gasData, expiration
        self.transaction_kind.serialize(serializer)
        self.sender.serialize(serializer)
        self.gas_data.serialize(serializer)
        self.expiration.serialize(serializer)
        
        self.logger.debug(f"Serialized transaction data V1: {list(serializer.to_bytes())}")
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> 'TransactionDataV1':
        """Deserialize transaction data V1."""
        transaction_kind = TransactionKind.deserialize(deserializer)
        sender = SuiAddress.deserialize(deserializer)
        gas_data = GasData.deserialize(deserializer)
        expiration = TransactionExpiration.deserialize(deserializer)
        
        return cls(
            transaction_kind=transaction_kind,
            sender=sender,
            gas_data=gas_data,
            expiration=expiration
        )
