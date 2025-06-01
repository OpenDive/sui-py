"""
Gas data structures for transaction execution.
"""

from dataclasses import dataclass
from typing import List
from ...bcs import Serializer, Deserializer, Serializable
from ...types import SuiAddress, ObjectRef

@dataclass  
class GasData(Serializable):
    """Gas data for transaction execution."""
    
    budget: str  # "1000000" in C# test
    price: str   # "1" in C# test  
    payment: List[ObjectRef]  # Payment object references
    owner: SuiAddress  # Gas owner address
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize gas data."""
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
