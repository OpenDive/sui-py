"""
Core BCS Deserializer implementation.

The Deserializer provides low-level binary reading operations for parsing BCS
(Binary Canonical Serialization) format data used by the Move language and Sui blockchain.
"""

import struct
from typing import Optional

from .exceptions import (
    DeserializationError, 
    InsufficientDataError, 
    InvalidDataError, 
    OverflowError
)


class Deserializer:
    """
    Core BCS deserializer for reading binary data in canonical format.
    
    This class handles the low-level details of decoding data according to the BCS
    specification, including proper endianness, variable-length decoding, and
    robust error handling for malformed data.
    
    The deserializer maintains a current position within the input data and
    provides methods for reading all BCS primitive types.
    """
    
    def __init__(self, data: bytes):
        """
        Initialize a new deserializer.
        
        Args:
            data: The binary data to deserialize
            
        Raises:
            DeserializationError: If data is not bytes
        """
        if not isinstance(data, (bytes, bytearray)):
            raise DeserializationError("Input data must be bytes or bytearray")
        
        self._data = bytes(data)  # Ensure immutable bytes
        self._position = 0
        
    def _ensure_available(self, needed_bytes: int) -> None:
        """
        Ensure the required number of bytes are available.
        
        Args:
            needed_bytes: Number of bytes needed
            
        Raises:
            InsufficientDataError: If not enough data is available
        """
        available = len(self._data) - self._position
        if available < needed_bytes:
            raise InsufficientDataError(needed_bytes, available, self._position)
    
    def read_u8(self) -> int:
        """
        Read an 8-bit unsigned integer.
        
        Returns:
            The decoded integer value (0-255)
            
        Raises:
            InsufficientDataError: If not enough data is available
            DeserializationError: If reading fails
        """
        try:
            self._ensure_available(1)
            value = self._data[self._position]
            self._position += 1
            return value
        except InsufficientDataError:
            raise
        except Exception as e:
            raise DeserializationError(f"Failed to read u8: {e}", self._position)
    
    def read_u16(self) -> int:
        """
        Read a 16-bit unsigned integer in little-endian format.
        
        Returns:
            The decoded integer value (0-65535)
            
        Raises:
            InsufficientDataError: If not enough data is available
            DeserializationError: If reading fails
        """
        try:
            self._ensure_available(2)
            value = struct.unpack_from('<H', self._data, self._position)[0]
            self._position += 2
            return value
        except InsufficientDataError:
            raise
        except Exception as e:
            raise DeserializationError(f"Failed to read u16: {e}", self._position)
    
    def read_u32(self) -> int:
        """
        Read a 32-bit unsigned integer in little-endian format.
        
        Returns:
            The decoded integer value (0-4294967295)
            
        Raises:
            InsufficientDataError: If not enough data is available
            DeserializationError: If reading fails
        """
        try:
            self._ensure_available(4)
            value = struct.unpack_from('<I', self._data, self._position)[0]
            self._position += 4
            return value
        except InsufficientDataError:
            raise
        except Exception as e:
            raise DeserializationError(f"Failed to read u32: {e}", self._position)
    
    def read_u64(self) -> int:
        """
        Read a 64-bit unsigned integer in little-endian format.
        
        Returns:
            The decoded integer value (0-18446744073709551615)
            
        Raises:
            InsufficientDataError: If not enough data is available
            DeserializationError: If reading fails
        """
        try:
            self._ensure_available(8)
            value = struct.unpack_from('<Q', self._data, self._position)[0]
            self._position += 8
            return value
        except InsufficientDataError:
            raise
        except Exception as e:
            raise DeserializationError(f"Failed to read u64: {e}", self._position)
    
    def read_u128(self) -> int:
        """
        Read a 128-bit unsigned integer in little-endian format.
        
        Returns:
            The decoded integer value (0-340282366920938463463374607431768211455)
            
        Raises:
            InsufficientDataError: If not enough data is available
            DeserializationError: If reading fails
        """
        try:
            self._ensure_available(16)
            # Read as two 64-bit parts (little-endian)
            low, high = struct.unpack_from('<QQ', self._data, self._position)
            self._position += 16
            return low | (high << 64)
        except InsufficientDataError:
            raise
        except Exception as e:
            raise DeserializationError(f"Failed to read u128: {e}", self._position)
    
    def read_u256(self) -> int:
        """
        Read a 256-bit unsigned integer in little-endian format.
        
        Returns:
            The decoded integer value (0-115792089237316195423570985008687907853269984665640564039457584007913129639935)
            
        Raises:
            InsufficientDataError: If not enough data is available
            DeserializationError: If reading fails
        """
        try:
            self._ensure_available(32)
            # Read as four 64-bit parts (little-endian)
            parts = struct.unpack_from('<QQQQ', self._data, self._position)
            self._position += 32
            
            result = 0
            for i, part in enumerate(parts):
                result |= part << (64 * i)
            return result
        except InsufficientDataError:
            raise
        except Exception as e:
            raise DeserializationError(f"Failed to read u256: {e}", self._position)
    
    def read_bool(self) -> bool:
        """
        Read a boolean value (1 byte: 0 for False, 1 for True).
        
        Returns:
            The decoded boolean value
            
        Raises:
            InsufficientDataError: If not enough data is available
            InvalidDataError: If the byte is not 0 or 1
        """
        value = self.read_u8()
        if value == 0:
            return False
        elif value == 1:
            return True
        else:
            raise InvalidDataError("Boolean value must be 0 or 1", value, self._position - 1)
    
    def read_bytes(self, length: int) -> bytes:
        """
        Read a fixed number of raw bytes.
        
        Args:
            length: Number of bytes to read
            
        Returns:
            The raw bytes
            
        Raises:
            InsufficientDataError: If not enough data is available
            DeserializationError: If length is negative
        """
        if length < 0:
            raise DeserializationError(f"Byte length must be non-negative, got {length}")
        
        try:
            self._ensure_available(length)
            data = self._data[self._position:self._position + length]
            self._position += length
            return data
        except InsufficientDataError:
            raise
        except Exception as e:
            raise DeserializationError(f"Failed to read bytes: {e}", self._position)
    
    def read_uleb128(self) -> int:
        """
        Read an unsigned integer using LEB128 (Little Endian Base 128) encoding.
        
        This is used for decoding vector lengths and option tags in BCS.
        
        Returns:
            The decoded non-negative integer
            
        Raises:
            InsufficientDataError: If not enough data is available
            InvalidDataError: If the encoding is invalid
            OverflowError: If the value is too large
        """
        result = 0
        shift = 0
        
        while True:
            if shift >= 64:  # Prevent excessive shifts
                raise OverflowError(result, "ULEB128", (1 << 64) - 1)
            
            byte = self.read_u8()
            result |= (byte & 0x7F) << shift
            
            if (byte & 0x80) == 0:
                break
            
            shift += 7
        
        return result
    
    def read_vector_length(self) -> int:
        """
        Read a vector length using ULEB128 encoding.
        
        Returns:
            The vector length (non-negative integer)
            
        Raises:
            InsufficientDataError: If not enough data is available
            InvalidDataError: If the encoding is invalid
        """
        return self.read_uleb128()
    
    def read_option_tag(self) -> bool:
        """
        Read an option tag (0 for None, 1 for Some).
        
        Returns:
            True if option contains a value, False if None
            
        Raises:
            InsufficientDataError: If not enough data is available
            InvalidDataError: If the tag is not 0 or 1
        """
        tag = self.read_u8()
        if tag == 0:
            return False
        elif tag == 1:
            return True
        else:
            raise InvalidDataError("Option tag must be 0 or 1", tag, self._position - 1)
    
    def remaining_bytes(self) -> int:
        """
        Get the number of bytes remaining to be read.
        
        Returns:
            Number of unread bytes
        """
        return len(self._data) - self._position
    
    def position(self) -> int:
        """
        Get the current read position.
        
        Returns:
            Current position in the data stream
        """
        return self._position
    
    def is_empty(self) -> bool:
        """
        Check if all data has been consumed.
        
        Returns:
            True if no more data to read, False otherwise
        """
        return self._position >= len(self._data)
    
    def peek_u8(self) -> Optional[int]:
        """
        Peek at the next byte without advancing the position.
        
        Returns:
            The next byte value, or None if no data available
        """
        if self.remaining_bytes() > 0:
            return self._data[self._position]
        return None
    
    def set_position(self, position: int) -> None:
        """
        Set the read position (for advanced use cases).
        
        Args:
            position: New position in the data stream
            
        Raises:
            DeserializationError: If position is invalid
        """
        if not (0 <= position <= len(self._data)):
            raise DeserializationError(f"Invalid position {position}, data length is {len(self._data)}")
        self._position = position 