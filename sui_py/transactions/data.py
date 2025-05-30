"""
Transaction data structures for complete transaction serialization.

These structures wrap around PTBs to create complete transaction data
that matches the C# Sui Unity SDK implementation.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import IntEnum

from ..bcs import Serializer, Deserializer, Serializable, Deserializable
from ..types import SuiAddress, ObjectRef
from .ptb import ProgrammableTransactionBlock


class TransactionType(IntEnum):
    """Transaction type enumeration."""
    V1 = 0


@dataclass
class TransactionExpiration(Serializable):
    """Transaction expiration data (currently empty in C# test)."""
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize transaction expiration."""
        # Looking at the C# expected bytes, this appears to be an enum/option type
        # The expected bytes suggest this is a "None" option (0 tag)
        serializer.write_u8(0)  # None variant
    
    @classmethod  
    def deserialize(cls, deserializer: Deserializer) -> 'TransactionExpiration':
        """Deserialize transaction expiration."""
        tag = deserializer.read_u8()  # Should be 0 for None
        return cls()


@dataclass  
class GasData(Serializable):
    """Gas data for transaction execution."""
    
    budget: str  # "1000000" in C# test
    price: str   # "1" in C# test  
    payment: List[ObjectRef]  # Payment object references
    owner: SuiAddress  # Gas owner address
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize gas data."""
        # From C#: GasData(budget, price, payment, owner)
        # Serialize in exact order from C# constructor
        
        # Serialize payment objects vector first (this seems to be the order in C# BCS)
        serializer.write_uleb128(len(self.payment))
        for payment_ref in self.payment:
            payment_ref.serialize(serializer)
            
        # Serialize owner address  
        self.owner.serialize(serializer)
        
        # Serialize budget as u64
        serializer.write_u64(int(self.budget))
        
        # Serialize price as u64
        serializer.write_u64(int(self.price))
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> 'GasData':
        """Deserialize gas data."""
        budget = str(deserializer.read_u64())
        price = str(deserializer.read_u64())
        
        # Read payment vector
        payment_count = deserializer.read_uleb128()
        payment = [ObjectRef.deserialize(deserializer) for _ in range(payment_count)]
        
        owner = SuiAddress.deserialize(deserializer)
        
        return cls(budget=budget, price=price, payment=payment, owner=owner)


class TransactionKindType(IntEnum):
    """Transaction kind type enumeration."""
    ProgrammableTransaction = 0


@dataclass
class TransactionKind(Serializable):
    """Transaction kind wrapper."""
    
    kind_type: TransactionKindType
    programmable_transaction: ProgrammableTransactionBlock
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize transaction kind."""
        # Serialize kind type (0 for ProgrammableTransaction)
        serializer.write_u8(self.kind_type.value)
        
        # Serialize the PTB
        self.programmable_transaction.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> 'TransactionKind':
        """Deserialize transaction kind."""
        kind_type = TransactionKindType(deserializer.read_u8())
        ptb = ProgrammableTransactionBlock.deserialize(deserializer)
        
        return cls(kind_type=kind_type, programmable_transaction=ptb)


@dataclass
class TransactionDataV1(Serializable):
    """Transaction data V1 structure."""
    
    sender: SuiAddress
    expiration: TransactionExpiration  
    gas_data: GasData
    transaction_kind: TransactionKind
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize transaction data V1."""
        # Match C# exact order: Transaction, Sender, GasData, Expiration
        self.transaction_kind.serialize(serializer)
        self.sender.serialize(serializer)
        self.gas_data.serialize(serializer)
        self.expiration.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> 'TransactionDataV1':
        """Deserialize transaction data V1."""
        sender = SuiAddress.deserialize(deserializer)
        expiration = TransactionExpiration.deserialize(deserializer)
        gas_data = GasData.deserialize(deserializer)
        transaction_kind = TransactionKind.deserialize(deserializer)
        
        return cls(
            sender=sender,
            expiration=expiration, 
            gas_data=gas_data,
            transaction_kind=transaction_kind
        )


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