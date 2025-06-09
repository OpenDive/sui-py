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
        
        # Serialize gas data with TypeScript-compatible owner fallback
        # TypeScript SDK: `owner: prepareSuiAddress(this.gasData.owner ?? sender)`
        # This allows JSON to show owner: null while BCS uses sender as fallback
        self._serialize_gas_data_with_fallback(serializer)
        
        self.expiration.serialize(serializer)
        
        self.logger.debug(f"Serialized transaction data V1: {list(serializer.to_bytes())}")
    
    def _serialize_gas_data_with_fallback(self, serializer: Serializer) -> None:
        """
        Serialize gas data with owner fallback to match TypeScript SDK behavior.
        
        The TypeScript SDK keeps gasData.owner as null in the JSON representation
        but applies fallback logic during BCS serialization: `owner ?? sender`.
        This method replicates that exact behavior for compatibility.
        
        See: typescript/src/transactions/TransactionData.ts line 179
        """
        # Apply TypeScript's exact fallback pattern: owner ?? sender
        resolved_owner = self.gas_data.owner or self.sender
        
        # Manual serialization matching GasData.serialize() but with resolved owner
        # Order: Payment, Owner, Price, Budget (matches C# and Rust implementations)
        
        # Serialize payment objects vector (sequence)
        serializer.write_uleb128(len(self.gas_data.payment))
        for payment_ref in self.gas_data.payment:
            payment_ref.serialize(serializer)
            
        # Serialize resolved owner address (applying fallback)
        resolved_owner.serialize(serializer)
        
        # Serialize price as u64
        serializer.write_u64(int(self.gas_data.price))
        
        # Serialize budget as u64
        serializer.write_u64(int(self.gas_data.budget))
    
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
