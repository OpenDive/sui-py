"""
Protocol definitions for BCS serialization and deserialization.

These protocols define the interface that all BCS-serializable types must implement,
providing type safety and ensuring consistent serialization behavior across the codebase.
"""

from typing import Protocol, TypeVar, Type
from typing_extensions import Self

# Forward declarations to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .serializer import Serializer
    from .deserializer import Deserializer


class Serializable(Protocol):
    """
    Protocol for types that can be serialized to BCS format.
    
    Any type implementing this protocol can be serialized using a BCS Serializer.
    The serialization should write the object's data to the serializer in the
    correct BCS format according to the Move specification.
    
    Example:
        class SuiAddress:
            def serialize(self, serializer: Serializer) -> None:
                serializer.write_bytes(self._address_bytes)
    """
    
    def serialize(self, serializer: "Serializer") -> None:
        """
        Serialize this object using the provided serializer.
        
        This method should write the object's data to the serializer in BCS format.
        The implementation should handle all the object's fields in the correct order
        and delegate to nested objects as needed.
        
        Args:
            serializer: The BCS serializer to write data to
            
        Raises:
            SerializationError: If serialization fails due to invalid data
        """
        ...


class Deserializable(Protocol):
    """
    Protocol for types that can be deserialized from BCS format.
    
    Any type implementing this protocol can be deserialized using a BCS Deserializer.
    The deserialization should read the object's data from the deserializer and
    construct a new instance of the type.
    
    Example:
        class SuiAddress:
            @classmethod
            def deserialize(cls, deserializer: Deserializer) -> Self:
                address_bytes = deserializer.read_bytes(32)
                return cls(address_bytes)
    """
    
    @classmethod
    def deserialize(cls, deserializer: "Deserializer") -> Self:
        """
        Deserialize an instance of this type from the provided deserializer.
        
        This method should read the object's data from the deserializer in BCS format
        and construct a new instance. The implementation should handle all the object's
        fields in the same order as serialization.
        
        Args:
            deserializer: The BCS deserializer to read data from
            
        Returns:
            A new instance of this type constructed from the deserialized data
            
        Raises:
            DeserializationError: If deserialization fails due to invalid or insufficient data
            TypeMismatchError: If the data doesn't match the expected type schema
        """
        ...


# Type variable for deserializable types
T = TypeVar('T', bound=Deserializable)


class BcsSerializable(Serializable, Deserializable, Protocol):
    """
    Combined protocol for types that support both serialization and deserialization.
    
    This is a convenience protocol for types that implement both directions of BCS
    conversion. Most concrete types should implement this combined protocol.
    """
    pass


class SizedSerializable(Serializable, Protocol):
    """
    Protocol for serializable types that can provide their serialized size.
    
    This is useful for optimizing buffer allocation in the serializer,
    especially for types with known or easily calculated sizes.
    """
    
    def serialized_size(self) -> int:
        """
        Get the size in bytes that this object will occupy when serialized.
        
        Returns:
            The number of bytes this object will use in BCS format
        """
        ...


class VersionedDeserializable(Deserializable, Protocol):
    """
    Protocol for types that support versioned deserialization.
    
    This allows for schema evolution and backward compatibility by including
    version information in the deserialization process.
    """
    
    @classmethod
    def deserialize_versioned(cls, deserializer: "Deserializer", version: int) -> Self:
        """
        Deserialize with explicit version information.
        
        Args:
            deserializer: The BCS deserializer to read data from
            version: The schema version to use for deserialization
            
        Returns:
            A new instance of this type
            
        Raises:
            DeserializationError: If the version is not supported
        """
        ... 