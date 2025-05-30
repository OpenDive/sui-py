"""
Generic container types for BCS serialization.

This module provides reusable container types that can serialize and deserialize
collections of any BCS-serializable type, including vectors and options.
"""

from typing import TypeVar, Generic, List, Optional, Type, Callable
from typing_extensions import Self

from .protocols import Serializable, Deserializable
from .serializer import Serializer
from .deserializer import Deserializer
from .exceptions import DeserializationError, SerializationError

# Type variable for contained types
T = TypeVar('T', bound=Serializable)
U = TypeVar('U', bound=Deserializable)


class BcsVector(Generic[T]):
    """
    A BCS-serializable vector (dynamic array) container.
    
    This container can hold any type that implements the Serializable protocol
    and provides BCS-compliant serialization with a length prefix followed by elements.
    
    The serialization format is:
    - ULEB128 length
    - Elements in sequence (each element serialized according to its type)
    """
    
    def __init__(self, elements: List[T]):
        """
        Initialize a BCS vector.
        
        Args:
            elements: List of elements to store in the vector
        """
        self.elements = elements
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the vector to BCS format.
        
        Args:
            serializer: The BCS serializer to write to
            
        Raises:
            SerializationError: If serialization fails
        """
        try:
            # Write the length as ULEB128
            serializer.write_vector_length(len(self.elements))
            
            # Write each element
            for element in self.elements:
                element.serialize(serializer)
        except Exception as e:
            raise SerializationError(f"Failed to serialize vector: {e}", "BcsVector")
    
    @classmethod
    def deserialize(
        cls, 
        deserializer: Deserializer, 
        element_deserializer: Callable[[Deserializer], U]
    ) -> "BcsVector[U]":
        """
        Deserialize a vector from BCS format.
        
        Args:
            deserializer: The BCS deserializer to read from
            element_deserializer: Function to deserialize individual elements
            
        Returns:
            A new BcsVector containing the deserialized elements
            
        Raises:
            DeserializationError: If deserialization fails
        """
        try:
            # Read the length
            length = deserializer.read_vector_length()
            
            # Read each element
            elements = []
            for i in range(length):
                try:
                    element = element_deserializer(deserializer)
                    elements.append(element)
                except Exception as e:
                    raise DeserializationError(f"Failed to deserialize vector element {i}: {e}")
            
            return cls(elements)
        except DeserializationError:
            raise
        except Exception as e:
            raise DeserializationError(f"Failed to deserialize vector: {e}")
    
    def __len__(self) -> int:
        """Get the number of elements in the vector."""
        return len(self.elements)
    
    def __getitem__(self, index: int) -> T:
        """Get an element by index."""
        return self.elements[index]
    
    def __setitem__(self, index: int, value: T) -> None:
        """Set an element by index."""
        self.elements[index] = value
    
    def __iter__(self):
        """Iterate over the elements."""
        return iter(self.elements)
    
    def append(self, element: T) -> None:
        """Add an element to the end of the vector."""
        self.elements.append(element)
    
    def extend(self, elements: List[T]) -> None:
        """Add multiple elements to the end of the vector."""
        self.elements.extend(elements)
    
    def to_list(self) -> List[T]:
        """Get the underlying list of elements."""
        return self.elements.copy()
    
    def __eq__(self, other) -> bool:
        """Check equality with another BcsVector."""
        if not isinstance(other, BcsVector):
            return False
        return self.elements == other.elements
    
    def __repr__(self) -> str:
        """String representation."""
        return f"BcsVector({self.elements!r})"


class BcsOption(Generic[T]):
    """
    A BCS-serializable optional value container.
    
    This container can hold any type that implements the Serializable protocol
    and provides BCS-compliant serialization for optional values.
    
    The serialization format is:
    - 1 byte tag: 0 for None, 1 for Some
    - If tag is 1, the value serialized according to its type
    """
    
    def __init__(self, value: Optional[T] = None):
        """
        Initialize a BCS option.
        
        Args:
            value: The optional value to store
        """
        self.value = value
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the option to BCS format.
        
        Args:
            serializer: The BCS serializer to write to
            
        Raises:
            SerializationError: If serialization fails
        """
        try:
            if self.value is None:
                serializer.write_option_tag(False)
            else:
                serializer.write_option_tag(True)
                self.value.serialize(serializer)
        except Exception as e:
            raise SerializationError(f"Failed to serialize option: {e}", "BcsOption")
    
    @classmethod
    def deserialize(
        cls, 
        deserializer: Deserializer, 
        value_deserializer: Callable[[Deserializer], U]
    ) -> "BcsOption[U]":
        """
        Deserialize an option from BCS format.
        
        Args:
            deserializer: The BCS deserializer to read from
            value_deserializer: Function to deserialize the value if present
            
        Returns:
            A new BcsOption containing the deserialized value (or None)
            
        Raises:
            DeserializationError: If deserialization fails
        """
        try:
            has_value = deserializer.read_option_tag()
            
            if has_value:
                value = value_deserializer(deserializer)
                return cls(value)
            else:
                return cls(None)
        except Exception as e:
            raise DeserializationError(f"Failed to deserialize option: {e}")
    
    def is_some(self) -> bool:
        """Check if the option contains a value."""
        return self.value is not None
    
    def is_none(self) -> bool:
        """Check if the option is None."""
        return self.value is None
    
    def unwrap(self) -> T:
        """
        Get the contained value.
        
        Returns:
            The contained value
            
        Raises:
            ValueError: If the option is None
        """
        if self.value is None:
            raise ValueError("Called unwrap on None option")
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        """
        Get the contained value or a default.
        
        Args:
            default: Value to return if option is None
            
        Returns:
            The contained value or the default
        """
        return self.value if self.value is not None else default
    
    def map(self, func: Callable[[T], U]) -> "BcsOption[U]":
        """
        Transform the contained value if present.
        
        Args:
            func: Function to apply to the value
            
        Returns:
            A new option with the transformed value
        """
        if self.value is None:
            return BcsOption(None)
        else:
            return BcsOption(func(self.value))
    
    @classmethod
    def some(cls, value: T) -> "BcsOption[T]":
        """Create an option containing a value."""
        return cls(value)
    
    @classmethod
    def none(cls) -> "BcsOption[T]":
        """Create an empty option."""
        return cls(None)
    
    def __eq__(self, other) -> bool:
        """Check equality with another BcsOption."""
        if not isinstance(other, BcsOption):
            return False
        return self.value == other.value
    
    def __repr__(self) -> str:
        """String representation."""
        if self.value is None:
            return "BcsOption(None)"
        else:
            return f"BcsOption({self.value!r})"


# Convenience factory functions
def bcs_vector(elements: List[T]) -> BcsVector[T]:
    """
    Create a BCS vector from a list of elements.
    
    Args:
        elements: List of elements
        
    Returns:
        A new BcsVector
    """
    return BcsVector(elements)


def bcs_option(value: Optional[T] = None) -> BcsOption[T]:
    """
    Create a BCS option from an optional value.
    
    Args:
        value: Optional value
        
    Returns:
        A new BcsOption
    """
    return BcsOption(value)


def bcs_some(value: T) -> BcsOption[T]:
    """
    Create a BCS option containing a value.
    
    Args:
        value: The value to wrap
        
    Returns:
        A new BcsOption containing the value
    """
    return BcsOption.some(value)


def bcs_none() -> BcsOption[None]:
    """
    Create an empty BCS option.
    
    Returns:
        A new empty BcsOption
    """
    return BcsOption.none() 