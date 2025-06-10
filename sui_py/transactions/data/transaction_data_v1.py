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
    def _deserialize_gas_data_with_fallback(cls, deserializer: Deserializer, sender: SuiAddress) -> GasData:
        """
        Deserialize gas data with custom logic that matches our custom serialization.
        
        This method reads gas data in the exact same order as _serialize_gas_data_with_fallback()
        writes it: Payment → Owner → Price → Budget
        
        The deserialized owner represents the resolved owner (after fallback), but we need to
        determine if it was originally null by comparing with sender. However, since the 
        TypeScript SDK always applies the fallback during serialization, we cannot distinguish
        between an explicitly set owner and a fallback owner from the serialized bytes alone.
        
        For round-trip compatibility, we set owner=None when the deserialized owner equals sender,
        assuming it was a fallback case. This matches TypeScript SDK's JSON representation.
        """
        # Read in the exact same order as serialization: Payment → Owner → Price → Budget
        
        # Read payment objects vector
        payment_count = deserializer.read_uleb128()
        payment = []
        for _ in range(payment_count):
            payment_ref = cls._deserialize_object_ref(deserializer)
            payment.append(payment_ref)
        
        # Read resolved owner address
        resolved_owner = SuiAddress.deserialize(deserializer)
        
        # Read price as u64
        price = str(deserializer.read_u64())
        
        # Read budget as u64  
        budget = str(deserializer.read_u64())
        
        # Determine original owner value for JSON representation compatibility
        # If resolved_owner equals sender, it was likely a fallback (owner was null)
        # This maintains TypeScript SDK's behavior where gasData.owner can be null in JSON
        original_owner = None if resolved_owner == sender else resolved_owner
        
        return GasData(
            budget=budget,
            price=price, 
            payment=payment,
            owner=original_owner
        )
    
    @classmethod
    def _deserialize_object_ref(cls, deserializer: Deserializer):
        """
        Helper method to deserialize ObjectRef.
        
        This avoids circular import issues by importing ObjectRef locally
        and matches the deserialization pattern used elsewhere.
        """
        from ...types import ObjectRef
        return ObjectRef.deserialize(deserializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> 'TransactionDataV1':
        """
        Deserialize transaction data V1.
        
        IMPORTANT: This uses custom gas data deserialization to match our custom
        serialization logic in _serialize_gas_data_with_fallback(). We cannot use
        standard GasData.deserialize() because it expects a different byte order
        than what our custom serialization produces.
        """
        transaction_kind = TransactionKind.deserialize(deserializer)
        sender = SuiAddress.deserialize(deserializer)
        
        # Use custom gas data deserialization that matches our custom serialization
        # Our serialization order: Payment → Owner → Price → Budget
        # Standard GasData.deserialize order: Budget → Price → Payment → Owner  
        gas_data = cls._deserialize_gas_data_with_fallback(deserializer, sender)
        
        expiration = TransactionExpiration.deserialize(deserializer)
        
        return cls(
            transaction_kind=transaction_kind,
            sender=sender,
            gas_data=gas_data,
            expiration=expiration
        )
