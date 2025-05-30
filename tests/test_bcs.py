#!/usr/bin/env python3
"""
Test suite for the BCS implementation.

This module tests the Binary Canonical Serialization (BCS) framework,
including primitive types, containers, and serialization/deserialization.
Based on test cases from the C# Sui Unity SDK for comprehensive coverage.
"""

import pytest
import sys
import os

# Add the parent directory to the path to import sui_py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sui_py.bcs import (
    # Core functions
    serialize, deserialize,
    # Primitive types
    U8, U16, U32, U64, U128, U256, Bool, Bytes, FixedBytes,
    # Container types
    BcsVector, BcsOption, bcs_vector, bcs_option, bcs_some, bcs_none,
    # Factory functions
    u8, u16, u32, u64, u128, u256, boolean, bytes_value, fixed_bytes,
    # Low-level access
    Serializer, Deserializer,
    # Exceptions
    OverflowError, InsufficientDataError, InvalidDataError, DeserializationError
)


class TestPrimitiveTypes:
    """Test cases for BCS primitive type serialization/deserialization."""
    
    def test_bool_true_ser_and_der(self):
        """Test Bool True serialization and deserialization (C# equivalent: BoolTrueSerAndDerTest)."""
        input_val = True
        bool_obj = Bool(input_val)
        data = serialize(bool_obj)
        
        # Should be exactly 1 byte with value 1
        assert len(data) == 1
        assert data == b'\x01'
        
        # Test deserialization
        restored = deserialize(data, Bool.deserialize)
        assert restored.value == input_val
        assert restored.value is True
    
    def test_bool_false_ser_and_der(self):
        """Test Bool False serialization and deserialization (C# equivalent: BoolFalseSerAndDerTest)."""
        input_val = False
        bool_obj = Bool(input_val)
        data = serialize(bool_obj)
        
        # Should be exactly 1 byte with value 0
        assert len(data) == 1
        assert data == b'\x00'
        
        # Test deserialization
        restored = deserialize(data, Bool.deserialize)
        assert restored.value == input_val
        assert restored.value is False
    
    def test_bool_error_ser_and_der(self):
        """Test Bool error handling for invalid data (C# equivalent: BoolErrorSerAndDerTest)."""
        # Serialize a U8 with invalid bool value (32)
        invalid_byte = U8(32)
        data = serialize(invalid_byte)
        
        # Should be 1 byte with value 32
        assert len(data) == 1
        assert data == b'\x20'  # 32 in hex
        
        # Trying to deserialize as Bool should raise InvalidDataError
        with pytest.raises(InvalidDataError):
            deserialize(data, Bool.deserialize)
    
    def test_byte_array_ser_and_der(self):
        """Test byte array serialization and deserialization (C# equivalent: ByteArraySerAndDerTest)."""
        input_data = "1234567890".encode('utf-8')
        bytes_obj = Bytes(input_data)
        data = serialize(bytes_obj)
        
        # Should include length prefix + actual data
        assert len(data) > len(input_data)
        
        # Test deserialization
        restored = deserialize(data, Bytes.deserialize)
        assert restored.value == input_data
        
        # Test that the data matches exactly
        assert input_data == restored.value
    
    def test_string_ser_and_der(self):
        """Test string serialization and deserialization (C# equivalent: StringSerAndDerTest)."""
        input_str = "1234567890"
        input_bytes = input_str.encode('utf-8')
        bytes_obj = Bytes(input_bytes)
        data = serialize(bytes_obj)
        
        # Test deserialization
        restored = deserialize(data, Bytes.deserialize)
        output_str = restored.value.decode('utf-8')
        
        assert output_str == input_str
    
    def test_byte_ser_and_der(self):
        """Test U8/byte serialization and deserialization (C# equivalent: ByteSerAndDerTest)."""
        input_val = 15
        u8_obj = U8(input_val)
        data = serialize(u8_obj)
        
        # U8 should be exactly 1 byte
        assert len(data) == 1
        assert data == b'\x0f'  # 15 in hex
        
        # Test deserialization
        restored = deserialize(data, U8.deserialize)
        assert restored.value == input_val
    
    def test_ushort_ser_and_der(self):
        """Test U16/ushort serialization and deserialization (C# equivalent: UShortSerAndDerTest)."""
        input_val = 11115  # From C# test: 111_15
        u16_obj = U16(input_val)
        data = serialize(u16_obj)
        
        # U16 should be exactly 2 bytes (little-endian)
        assert len(data) == 2
        
        # Test deserialization
        restored = deserialize(data, U16.deserialize)
        assert restored.value == input_val
    
    def test_uint_ser_and_der(self):
        """Test U32/uint serialization and deserialization (C# equivalent: UIntSerAndDerTest)."""
        input_val = 1111111115  # From C# test: 1_111_111_115
        u32_obj = U32(input_val)
        data = serialize(u32_obj)
        
        # U32 should be exactly 4 bytes (little-endian)
        assert len(data) == 4
        
        # Test deserialization
        restored = deserialize(data, U32.deserialize)
        assert restored.value == input_val
    
    def test_ulong_ser_and_der(self):
        """Test U64/ulong serialization and deserialization (C# equivalent: ULongSerAndDerTest)."""
        input_val = 1111111111111111115  # From C# test: 1_111_111_111_111_111_115
        u64_obj = U64(input_val)
        data = serialize(u64_obj)
        
        # U64 should be exactly 8 bytes (little-endian)
        assert len(data) == 8
        
        # Test deserialization
        restored = deserialize(data, U64.deserialize)
        assert restored.value == input_val
    
    def test_uint128_big_integer_ser_and_der(self):
        """Test U128 with BigInteger serialization and deserialization (C# equivalent: UInt128BigIntegerSerAndDerTest)."""
        # From C# test: "1111111111111111111111111111111111115"
        input_val = int("1111111111111111111111111111111111115")
        u128_obj = U128(input_val)
        data = serialize(u128_obj)
        
        # U128 should be exactly 16 bytes
        assert len(data) == 16
        
        # Test deserialization
        restored = deserialize(data, U128.deserialize)
        assert restored.value == input_val
    
    def test_uint256_big_integer_ser_and_der(self):
        """Test U256 with BigInteger serialization and deserialization (C# equivalent: UInt256BigIntegerSerAndDerTest)."""
        # From C# test: "111111111111111111111111111111111111111111111111111111111111111111111111111115"
        input_val = int("111111111111111111111111111111111111111111111111111111111111111111111111111115")
        u256_obj = U256(input_val)
        data = serialize(u256_obj)
        
        # U256 should be exactly 32 bytes
        assert len(data) == 32
        
        # Test deserialization
        restored = deserialize(data, U256.deserialize)
        assert restored.value == input_val
    
    def test_uleb128_ser_and_der(self):
        """Test ULEB128 encoding/decoding directly (C# equivalent: ULeb128SerAndDerTest)."""
        input_val = 1111111115  # From C# test: 1_111_111_115
        
        # Test using low-level serializer for ULEB128
        serializer = Serializer()
        serializer.serialize_uleb128(input_val)
        data = serializer.to_bytes()
        
        # Test deserialization
        deserializer = Deserializer(data)
        output_val = deserializer.deserialize_uleb128()
        
        assert input_val == output_val
    
    def test_u8_serialization(self):
        """Test U8 serialization and deserialization."""
        value = U8(255)
        data = serialize(value)
        
        # U8 should be exactly 1 byte
        assert len(data) == 1
        assert data == b'\xff'
        
        # Test deserialization
        restored = deserialize(data, U8.deserialize)
        assert restored.value == 255
        assert isinstance(restored, U8)
    
    def test_u16_serialization(self):
        """Test U16 serialization and deserialization."""
        value = U16(65535)
        data = serialize(value)
        
        # U16 should be exactly 2 bytes (little-endian)
        assert len(data) == 2
        assert data == b'\xff\xff'
        
        # Test deserialization
        restored = deserialize(data, U16.deserialize)
        assert restored.value == 65535
    
    def test_u32_serialization(self):
        """Test U32 serialization and deserialization."""
        value = U32(0x12345678)
        data = serialize(value)
        
        # U32 should be exactly 4 bytes (little-endian)
        assert len(data) == 4
        assert data == b'\x78\x56\x34\x12'
        
        # Test deserialization
        restored = deserialize(data, U32.deserialize)
        assert restored.value == 0x12345678
    
    def test_u64_serialization(self):
        """Test U64 serialization and deserialization."""
        value = U64(12345)
        data = serialize(value)
        
        # U64 should be exactly 8 bytes
        assert len(data) == 8
        
        # Test deserialization
        restored = deserialize(data, U64.deserialize)
        assert restored.value == 12345
    
    def test_u128_serialization(self):
        """Test U128 serialization and deserialization."""
        value = U128(0x123456789abcdef0fedcba9876543210)
        data = serialize(value)
        
        # U128 should be exactly 16 bytes
        assert len(data) == 16
        
        # Test deserialization
        restored = deserialize(data, U128.deserialize)
        assert restored.value == 0x123456789abcdef0fedcba9876543210
    
    def test_u256_serialization(self):
        """Test U256 serialization and deserialization."""
        large_value = (1 << 255) - 1  # Large but valid U256
        value = U256(large_value)
        data = serialize(value)
        
        # U256 should be exactly 32 bytes
        assert len(data) == 32
        
        # Test deserialization
        restored = deserialize(data, U256.deserialize)
        assert restored.value == large_value
    
    def test_bool_serialization(self):
        """Test Bool serialization and deserialization."""
        # Test True
        true_val = Bool(True)
        true_data = serialize(true_val)
        assert len(true_data) == 1
        assert true_data == b'\x01'
        
        restored_true = deserialize(true_data, Bool.deserialize)
        assert restored_true.value is True
        
        # Test False
        false_val = Bool(False)
        false_data = serialize(false_val)
        assert len(false_data) == 1
        assert false_data == b'\x00'
        
        restored_false = deserialize(false_data, Bool.deserialize)
        assert restored_false.value is False
    
    def test_bytes_serialization(self):
        """Test Bytes serialization and deserialization."""
        test_data = b"hello world"
        value = Bytes(test_data)
        data = serialize(value)
        
        # Should have length prefix + data
        assert len(data) > len(test_data)
        
        # Test deserialization
        restored = deserialize(data, Bytes.deserialize)
        assert restored.value == test_data
    
    def test_fixed_bytes_serialization(self):
        """Test FixedBytes serialization and deserialization."""
        test_data = b"12345678"  # 8 bytes
        value = FixedBytes(test_data, 8)
        data = serialize(value)
        
        # Should be exactly the data (no length prefix)
        assert len(data) == 8
        assert data == test_data
        
        # Test deserialization
        restored = deserialize(data, lambda d: FixedBytes.deserialize(d, 8))
        assert restored.value == test_data
        assert restored.expected_length == 8


class TestContainerTypes:
    """Test cases for BCS container type serialization/deserialization."""
    
    def test_sequence_ser_and_der(self):
        """Test Sequence/Vector serialization and deserialization (C# equivalent: SequenceSerAndDerTest)."""
        # Test vector of strings (equivalent to C# Sequence of BString)
        input_strings = ["a", "abc", "def", "ghi"]
        string_bytes = [Bytes(s.encode('utf-8')) for s in input_strings]
        vector = bcs_vector(string_bytes)
        data = serialize(vector)
        
        # Test deserialization
        restored = deserialize(data, lambda d: BcsVector.deserialize(d, Bytes.deserialize))
        
        # Verify the restored vector matches
        assert len(restored) == len(input_strings)
        restored_strings = [elem.value.decode('utf-8') for elem in restored.elements]
        assert restored_strings == input_strings
        
        # Test equality (like C# Equals method)
        assert all(original == restored for original, restored in zip(input_strings, restored_strings))
    
    def test_vector_serialization(self):
        """Test BcsVector serialization and deserialization."""
        elements = [U8(1), U8(2), U8(3)]
        vector = bcs_vector(elements)
        data = serialize(vector)
        
        # Should have length prefix + element data
        assert len(data) > 3
        
        # Test deserialization
        restored = deserialize(data, lambda d: BcsVector.deserialize(d, U8.deserialize))
        assert len(restored) == 3
        assert [elem.value for elem in restored.elements] == [1, 2, 3]
    
    def test_empty_vector_serialization(self):
        """Test empty BcsVector serialization."""
        vector = bcs_vector([])
        data = serialize(vector)
        
        # Should just be the length prefix (0)
        assert len(data) == 1
        assert data == b'\x00'
        
        # Test deserialization
        restored = deserialize(data, lambda d: BcsVector.deserialize(d, U8.deserialize))
        assert len(restored) == 0
    
    def test_option_some_serialization(self):
        """Test BcsOption(Some) serialization and deserialization."""
        option = bcs_some(U32(999))
        data = serialize(option)
        
        # Should have tag (1) + value data
        assert len(data) == 5  # 1 byte tag + 4 bytes U32
        assert data[0] == 1  # Some tag
        
        # Test deserialization
        restored = deserialize(data, lambda d: BcsOption.deserialize(d, U32.deserialize))
        assert restored.is_some()
        assert restored.unwrap().value == 999
    
    def test_option_none_serialization(self):
        """Test BcsOption(None) serialization and deserialization."""
        option = bcs_none()
        data = serialize(option)
        
        # Should just be the None tag
        assert len(data) == 1
        assert data == b'\x00'
        
        # Test deserialization
        restored = deserialize(data, lambda d: BcsOption.deserialize(d, U32.deserialize))
        assert restored.is_none()
    
    def test_nested_containers(self):
        """Test nested container serialization."""
        # Vector of options
        elements = [bcs_some(U8(1)), bcs_none(), bcs_some(U8(3))]
        vector = bcs_vector(elements)
        data = serialize(vector)
        
        # Test deserialization
        restored = deserialize(
            data, 
            lambda d: BcsVector.deserialize(
                d, 
                lambda inner_d: BcsOption.deserialize(inner_d, U8.deserialize)
            )
        )
        
        assert len(restored) == 3
        assert restored[0].is_some() and restored[0].unwrap().value == 1
        assert restored[1].is_none()
        assert restored[2].is_some() and restored[2].unwrap().value == 3


class TestErrorHandling:
    """Test cases for BCS error handling."""
    
    def test_overflow_errors(self):
        """Test overflow validation in primitive types."""
        with pytest.raises(OverflowError):
            U8(256)  # Too large for U8
        
        with pytest.raises(OverflowError):
            U16(65536)  # Too large for U16
        
        with pytest.raises(OverflowError):
            U32(4294967296)  # Too large for U32
    
    def test_insufficient_data_error(self):
        """Test insufficient data error during deserialization."""
        incomplete_data = b'\x01'  # Only 1 byte, but trying to read U32
        
        with pytest.raises(InsufficientDataError):
            deserialize(incomplete_data, U32.deserialize)
    
    def test_invalid_bool_data(self):
        """Test invalid boolean data."""
        invalid_bool_data = b'\x02'  # Invalid boolean value (must be 0 or 1)
        
        with pytest.raises(InvalidDataError):
            deserialize(invalid_bool_data, Bool.deserialize)
    
    def test_invalid_option_tag(self):
        """Test invalid option tag."""
        invalid_option_data = b'\x02'  # Invalid option tag (must be 0 or 1)
        
        with pytest.raises(DeserializationError):
            deserialize(invalid_option_data, lambda d: BcsOption.deserialize(d, U8.deserialize))


class TestLEB128Encoding:
    """Test cases for ULEB128 encoding used in vectors and options."""
    
    def test_small_vector_length(self):
        """Test vector with small length (single byte ULEB128)."""
        elements = [U8(i) for i in range(5)]  # 5 elements
        vector = bcs_vector(elements)
        data = serialize(vector)
        
        # First byte should be 5 (length)
        assert data[0] == 5
        
        # Test round-trip
        restored = deserialize(data, lambda d: BcsVector.deserialize(d, U8.deserialize))
        assert len(restored) == 5
    
    def test_large_vector_length(self):
        """Test vector with large length (multi-byte ULEB128)."""
        # Create a vector with 200 elements (requires 2-byte ULEB128)
        elements = [U8(i % 256) for i in range(200)]
        vector = bcs_vector(elements)
        data = serialize(vector)
        
        # First two bytes should encode 200 in ULEB128
        # 200 = 0xC8 = 0b11001000
        # ULEB128: 0b11001000, 0b00000001 = 0xC8, 0x01
        assert data[0] == 0xC8
        assert data[1] == 0x01
        
        # Test round-trip
        restored = deserialize(data, lambda d: BcsVector.deserialize(d, U8.deserialize))
        assert len(restored) == 200


def test_convenience_functions():
    """Test convenience serialization functions."""
    # Test top-level serialize function
    value = U64(42)
    data = serialize(value)
    assert len(data) == 8
    
    # Test top-level deserialize function
    restored = deserialize(data, U64.deserialize)
    assert restored.value == 42


def test_factory_functions():
    """Test primitive factory functions."""
    # Test that factory functions work
    assert u8(255).value == 255
    assert u16(1000).value == 1000
    assert u32(100000).value == 100000
    assert u64(1000000).value == 1000000
    assert boolean(True).value is True
    assert bytes_value(b"test").value == b"test"


def test_basic_functionality():
    """Basic smoke test for BCS functionality."""
    print("Testing BCS implementation...")
    
    # Test primitive types
    value = U64(12345)
    data = serialize(value)
    print(f"U64(12345) serialized to {len(data)} bytes: {data.hex()}")
    
    restored = deserialize(data, U64.deserialize)
    assert restored.value == 12345
    print(f"Deserialized back to: {restored.value}")
    
    # Test vectors
    vector = bcs_vector([U8(1), U8(2), U8(3)])
    vector_data = serialize(vector)
    print(f"Vector serialized to {len(vector_data)} bytes: {vector_data.hex()}")
    
    # Test options
    option_some = bcs_some(U32(999))
    option_data = serialize(option_some)
    print(f"Option(Some) serialized to {len(option_data)} bytes: {option_data.hex()}")
    
    option_none = bcs_none()
    none_data = serialize(option_none)
    print(f"Option(None) serialized to {len(none_data)} bytes: {none_data.hex()}")
    
    print("✓ All basic tests passed!")


if __name__ == "__main__":
    # Run basic functionality test
    test_basic_functionality()
    print("\n🎉 BCS implementation is working correctly!") 