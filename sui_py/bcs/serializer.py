"""
Core BCS Serializer implementation.

The Serializer provides low-level binary writing operations following the BCS
(Binary Canonical Serialization) specification used by the Move language and Sui blockchain.
"""

import struct
from typing import Optional

from .exceptions import SerializationError, OverflowError


class Serializer:
    """
    Core BCS serializer for writing binary data in canonical format.
    
    This class handles the low-level details of encoding data according to the BCS
    specification, including proper endianness, variable-length encoding, and
    deterministic output generation.
    
    The serializer maintains an internal byte buffer that grows as needed and
    provides methods for writing all BCS primitive types.
    """
    
    def __init__(self, initial_capacity: int = 1024):
        """
        Initialize a new serializer.
        
        Args:
            initial_capacity: Initial size of the internal buffer in bytes
        """
        self._buffer = bytearray(initial_capacity)
        self._position = 0
        
    def _ensure_capacity(self, needed_bytes: int) -> None:
        """
        Ensure the buffer has enough capacity for the requested bytes.
        
        Args:
            needed_bytes: Number of additional bytes needed
        """
        required_size = self._position + needed_bytes
        if required_size > len(self._buffer):
            # Grow buffer by at least 50% or required size, whichever is larger
            new_size = max(required_size, len(self._buffer) * 3 // 2)
            self._buffer.extend(bytearray(new_size - len(self._buffer)))
    
    def write_u8(self, value: int) -> None:
        """
        Write an 8-bit unsigned integer.
        
        Args:
            value: Value to write (0-255)
            
        Raises:
            OverflowError: If value exceeds u8 range
            SerializationError: If writing fails
        """
        if not (0 <= value <= 255):
            raise OverflowError(value, "u8", 255)
        
        try:
            self._ensure_capacity(1)
            self._buffer[self._position] = value
            self._position += 1
        except Exception as e:
            raise SerializationError(f"Failed to write u8: {e}")
    
    def write_u16(self, value: int) -> None:
        """
        Write a 16-bit unsigned integer in little-endian format.
        
        Args:
            value: Value to write (0-65535)
            
        Raises:
            OverflowError: If value exceeds u16 range
            SerializationError: If writing fails
        """
        if not (0 <= value <= 65535):
            raise OverflowError(value, "u16", 65535)
        
        try:
            self._ensure_capacity(2)
            struct.pack_into('<H', self._buffer, self._position, value)
            self._position += 2
        except Exception as e:
            raise SerializationError(f"Failed to write u16: {e}")
    
    def write_u32(self, value: int) -> None:
        """
        Write a 32-bit unsigned integer in little-endian format.
        
        Args:
            value: Value to write (0-4294967295)
            
        Raises:
            OverflowError: If value exceeds u32 range
            SerializationError: If writing fails
        """
        if not (0 <= value <= 4294967295):
            raise OverflowError(value, "u32", 4294967295)
        
        try:
            self._ensure_capacity(4)
            struct.pack_into('<I', self._buffer, self._position, value)
            self._position += 4
        except Exception as e:
            raise SerializationError(f"Failed to write u32: {e}")
    
    def write_u64(self, value: int) -> None:
        """
        Write a 64-bit unsigned integer in little-endian format.
        
        Args:
            value: Value to write (0-18446744073709551615)
            
        Raises:
            OverflowError: If value exceeds u64 range
            SerializationError: If writing fails
        """
        if not (0 <= value <= 18446744073709551615):
            raise OverflowError(value, "u64", 18446744073709551615)
        
        try:
            self._ensure_capacity(8)
            struct.pack_into('<Q', self._buffer, self._position, value)
            self._position += 8
        except Exception as e:
            raise SerializationError(f"Failed to write u64: {e}")
    
    def write_u128(self, value: int) -> None:
        """
        Write a 128-bit unsigned integer in little-endian format.
        
        Args:
            value: Value to write (0-340282366920938463463374607431768211455)
            
        Raises:
            OverflowError: If value exceeds u128 range
            SerializationError: If writing fails
        """
        max_u128 = (1 << 128) - 1
        if not (0 <= value <= max_u128):
            raise OverflowError(value, "u128", max_u128)
        
        try:
            self._ensure_capacity(16)
            # Split into two 64-bit parts (little-endian)
            low = value & 0xFFFFFFFFFFFFFFFF
            high = (value >> 64) & 0xFFFFFFFFFFFFFFFF
            struct.pack_into('<QQ', self._buffer, self._position, low, high)
            self._position += 16
        except Exception as e:
            raise SerializationError(f"Failed to write u128: {e}")
    
    def write_u256(self, value: int) -> None:
        """
        Write a 256-bit unsigned integer in little-endian format.
        
        Args:
            value: Value to write (0-115792089237316195423570985008687907853269984665640564039457584007913129639935)
            
        Raises:
            OverflowError: If value exceeds u256 range
            SerializationError: If writing fails
        """
        max_u256 = (1 << 256) - 1
        if not (0 <= value <= max_u256):
            raise OverflowError(value, "u256", max_u256)
        
        try:
            self._ensure_capacity(32)
            # Split into four 64-bit parts (little-endian)
            parts = []
            for i in range(4):
                parts.append((value >> (64 * i)) & 0xFFFFFFFFFFFFFFFF)
            struct.pack_into('<QQQQ', self._buffer, self._position, *parts)
            self._position += 32
        except Exception as e:
            raise SerializationError(f"Failed to write u256: {e}")
    
    def write_bool(self, value: bool) -> None:
        """
        Write a boolean value (1 byte: 0 for False, 1 for True).
        
        Args:
            value: Boolean value to write
            
        Raises:
            SerializationError: If writing fails
        """
        self.write_u8(1 if value else 0)
    
    def write_bytes(self, data: bytes) -> None:
        """
        Write raw bytes without length prefix.
        
        Args:
            data: Bytes to write
            
        Raises:
            SerializationError: If writing fails
        """
        if not isinstance(data, (bytes, bytearray)):
            raise SerializationError("Data must be bytes or bytearray")
        
        try:
            data_len = len(data)
            self._ensure_capacity(data_len)
            self._buffer[self._position:self._position + data_len] = data
            self._position += data_len
        except Exception as e:
            raise SerializationError(f"Failed to write bytes: {e}")
    
    def write_uleb128(self, value: int) -> None:
        """
        Write an unsigned integer using LEB128 (Little Endian Base 128) encoding.
        
        This is used for encoding vector lengths and option tags in BCS.
        
        Args:
            value: Non-negative integer to encode
            
        Raises:
            SerializationError: If value is negative or writing fails
        """
        if value < 0:
            raise SerializationError(f"ULEB128 value must be non-negative, got {value}")
        
        try:
            while value >= 128:
                self.write_u8((value & 0x7F) | 0x80)
                value >>= 7
            self.write_u8(value & 0x7F)
        except Exception as e:
            raise SerializationError(f"Failed to write ULEB128: {e}")
    
    def write_vector_length(self, length: int) -> None:
        """
        Write a vector length using ULEB128 encoding.
        
        Args:
            length: Vector length (must be non-negative)
            
        Raises:
            SerializationError: If length is negative
        """
        if length < 0:
            raise SerializationError(f"Vector length must be non-negative, got {length}")
        self.write_uleb128(length)
    
    def write_option_tag(self, is_some: bool) -> None:
        """
        Write an option tag (0 for None, 1 for Some).
        
        Args:
            is_some: True if option contains a value, False if None
        """
        self.write_u8(1 if is_some else 0)
    
    def to_bytes(self) -> bytes:
        """
        Get the serialized data as bytes.
        
        Returns:
            The serialized data as a bytes object
        """
        return bytes(self._buffer[:self._position])
    
    def clear(self) -> None:
        """
        Clear the serializer buffer and reset position.
        
        This allows reusing the same serializer instance for multiple serializations.
        """
        self._position = 0
    
    def size(self) -> int:
        """
        Get the current size of serialized data.
        
        Returns:
            Number of bytes written to the serializer
        """
        return self._position
    
    def remaining_capacity(self) -> int:
        """
        Get the remaining capacity in the buffer.
        
        Returns:
            Number of bytes available before buffer needs to grow
        """
        return len(self._buffer) - self._position 