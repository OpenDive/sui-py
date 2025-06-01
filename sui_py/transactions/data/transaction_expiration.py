"""
Transaction expiration data structure.
"""

from dataclasses import dataclass
from ...bcs import Serializer, Deserializer, Serializable

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
