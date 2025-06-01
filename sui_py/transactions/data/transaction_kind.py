"""
Transaction kind structures and types.
"""

from dataclasses import dataclass
from enum import IntEnum
from ...bcs import Serializer, Deserializer, Serializable
from ..ptb import ProgrammableTransactionBlock

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
