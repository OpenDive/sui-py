"""
Object reference argument implementation.
"""

from dataclasses import dataclass
from typing import Optional, Union
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

    @classmethod 
    def from_object_ref(cls, object_id: str, version: int, digest: str) -> "ObjectArgument":
        """
        Create an ObjectArgument from a complete object reference.
        
        Args:
            object_id: The object ID
            version: The version number
            digest: The object digest
            
        Returns:
            A new ObjectArgument
        """
        from ..utils import validate_object_id
        normalized_id = validate_object_id(object_id)
        object_ref = ObjectRef(
            object_id=normalized_id,
            version=version,
            digest=digest
        )
        return cls(object_ref)


@dataclass(frozen=True)
class UnresolvedObjectArgument(BcsSerializable):
    """
    Unresolved object reference argument.
    
    This represents an object that needs to be resolved (version/digest fetched)
    before the transaction can be built. During the build process, this will be
    converted to a regular ObjectArgument.
    """
    object_id: str
    version: Optional[int] = None
    digest: Optional[str] = None
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Unresolved objects cannot be serialized directly.
        They must be resolved first during the build process.
        """
        raise RuntimeError(
            f"Cannot serialize unresolved object {self.object_id}. "
            "Call build_async() to resolve objects before serialization."
        )
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Unresolved objects cannot be deserialized."""
        raise RuntimeError("UnresolvedObjectArgument cannot be deserialized")

    def is_resolved(self) -> bool:
        """Check if this object has all required fields."""
        return self.version is not None and self.digest is not None

    def to_resolved(self, version: int, digest: str) -> ObjectArgument:
        """Convert to a resolved ObjectArgument."""
        return ObjectArgument.from_object_ref(self.object_id, version, digest)


def object_arg(object_id: str, version: Optional[int] = None, digest: Optional[str] = None) -> Union[ObjectArgument, UnresolvedObjectArgument]:
    """Create an object argument from an object ID."""
    if version is not None and digest is not None:
        return ObjectArgument.from_object_ref(object_id, version, digest)
    else:
        from ..utils import validate_object_id
        normalized_id = validate_object_id(object_id)
        return UnresolvedObjectArgument(object_id=normalized_id, version=version, digest=digest)
