"""
Gas data structures for transaction execution.
"""

from dataclasses import dataclass
from typing import List, Optional
from ...bcs import Serializer, Deserializer, Serializable
from ...types import SuiAddress, ObjectRef

@dataclass  
class GasData(Serializable):
    """Gas data for transaction execution."""
    
    budget: str  # "1000000" in C# test
    price: str   # "1" in C# test  
    payment: List[ObjectRef]  # Payment object references
    owner: Optional[SuiAddress]  # Gas owner address (can be None)
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize gas data.
        
        Note: This method requires owner to be set. For TypeScript SDK compatibility
        where owner can be null and needs fallback to sender, use the custom
        serialization in TransactionDataV1._serialize_gas_data_with_fallback().
        """
        if self.owner is None:
            raise ValueError(
                "GasData owner is None. For TypeScript SDK compatibility with null owners, "
                "use TransactionDataV1._serialize_gas_data_with_fallback() which applies "
                "the 'owner ?? sender' fallback pattern during serialization."
            )
        
        # Match C# exact order: Payment, Owner, Price, Budget
        
        # Serialize payment objects vector (sequence)
        serializer.write_uleb128(len(self.payment))
        for payment_ref in self.payment:
            payment_ref.serialize(serializer)
            
        # Serialize owner address  
        self.owner.serialize(serializer)
        
        # Serialize price as u64
        serializer.write_u64(int(self.price))
        
        # Serialize budget as u64
        serializer.write_u64(int(self.budget))
    
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
