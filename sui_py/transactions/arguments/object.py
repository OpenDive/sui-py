"""
Object reference argument implementation.
"""

from dataclasses import dataclass
from typing import Optional
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer
from ...types import ObjectRef


@dataclass(frozen=True)
class ObjectArgument(BcsSerializable):
    """
    Object reference argument.
    
    Object arguments represent references to on-chain objects,
    including owned objects, shared objects, and immutable objects.
    """
    object_ref: ObjectRef
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize as Object CallArg (tag 1 + object ref type + object ref)."""
        serializer.write_u8(1)  # Object variant
        # ObjectRefType.ImmOrOwned (0) vs ObjectRefType.Shared (1)
        serializer.write_u8(0)  # Use variant 0 (ImmOrOwned) for regular objects
        self.object_ref.serialize(serializer)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize an object argument."""
        object_ref = ObjectRef.deserialize(deserializer)
        return cls(object_ref)
    
    @classmethod
    def from_object_id(cls, object_id: str, version: Optional[int] = None, digest: Optional[str] = None) -> "ObjectArgument":
        """
        Create an ObjectArgument from an object ID.
        
        Args:
            object_id: The object ID
            version: Optional version number
            digest: Optional object digest
            
        Returns:
            A new ObjectArgument
        """
        from ..utils import validate_object_id
        normalized_id = validate_object_id(object_id)
        object_ref = ObjectRef(
            object_id=normalized_id,
            version=version or 0,
            digest=digest or ""
        )
        return cls(object_ref)


def object_arg(object_id: str, version: Optional[int] = None, digest: Optional[str] = None) -> ObjectArgument:
    """Create an object argument from an object ID."""
    return ObjectArgument.from_object_id(object_id, version, digest)
