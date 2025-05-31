#!/usr/bin/env python3
"""
BCS Test Suite - C# Unity SDK Equivalent

This module implements equivalent tests to the C# BCSTest.cs from the Sui Unity SDK,
providing cross-language validation of BCS serialization and deserialization.
"""

import pytest
import sys
import os

# Add the parent directory to the path to import sui_py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sui_py.bcs import (
    # Core serialization/deserialization
    Serializer, Deserializer, serialize, deserialize,
    # Primitive types
    U8, U16, U32, U64, U128, U256, Bool, Bytes,
    # Container types
    BcsVector,
    # Exceptions
    InvalidDataError, DeserializationError
)
from sui_py.transactions.utils import BcsString
from sui_py.types import SuiAddress
from sui_py.transactions import MoveCallCommand
from sui_py.transactions.arguments import (
    GasCoinArgument, NestedResultArgument, InputArgument, ResultArgument
)


class TestBCSCSharpEquivalent:
    """Test cases equivalent to C# Unity SDK BCSTest.cs"""
    
    def test_bool_true_ser_and_der(self):
        """
        Test Bool True serialization and deserialization.
        Equivalent to C# BoolTrueSerAndDerTest.
        """
        input_val = True
        
        # Serialize using the BCS system like C# does
        serializer = Serializer()
        bool_obj = Bool(input_val)
        bool_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_obj = Bool.deserialize(deserializer)
        output_val = output_obj.value
        
        assert input_val == output_val
        assert output_val is True
    
    def test_bool_false_ser_and_der(self):
        """
        Test Bool False serialization and deserialization.
        Equivalent to C# BoolFalseSerAndDerTest.
        """
        input_val = False
        
        # Serialize using the BCS system like C# does
        serializer = Serializer()
        bool_obj = Bool(input_val)
        bool_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_obj = Bool.deserialize(deserializer)
        output_val = output_obj.value
        
        assert input_val == output_val
        assert output_val is False
    
    def test_bool_error_ser_and_der(self):
        """
        Test Bool error handling for invalid data.
        Equivalent to C# BoolErrorSerAndDerTest.
        """
        input_val = 32  # Invalid bool value
        
        # Serialize a U8 with value 32
        serializer = Serializer()
        u8_obj = U8(input_val)
        u8_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Try to deserialize as Bool - should raise error
        deserializer = Deserializer(serialized_data)
        with pytest.raises(InvalidDataError):
            Bool.deserialize(deserializer)
    
    def test_byte_array_ser_and_der(self):
        """
        Test byte array serialization and deserialization.
        Equivalent to C# ByteArraySerAndDerTest.
        """
        input_data = "1234567890".encode('utf-8')
        
        # Serialize using the BCS system
        serializer = Serializer()
        bytes_obj = Bytes(input_data)
        bytes_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_obj = Bytes.deserialize(deserializer)
        output_data = output_obj.value
        
        assert input_data == output_data
    
    def test_sequence_ser_and_der(self):
        """
        Test sequence serialization and deserialization.
        Equivalent to C# SequenceSerAndDerTest.
        """
        # Create sequence of strings like C# test: "a", "abc", "def", "ghi"
        input_strings = ["a", "abc", "def", "ghi"]
        string_objects = [BcsString(s) for s in input_strings]
        
        # Create BcsVector of BcsString objects
        input_sequence = BcsVector(string_objects)
        
        # Serialize
        serializer = Serializer()
        input_sequence.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_sequence = BcsVector.deserialize(deserializer, BcsString.deserialize)
        
        # Compare sequences
        assert len(input_sequence.elements) == len(output_sequence.elements)
        for input_str, output_str in zip(input_sequence.elements, output_sequence.elements):
            assert input_str.value == output_str.value
    
    def test_string_ser_and_der(self):
        """
        Test string serialization and deserialization.
        Equivalent to C# StringSerAndDerTest.
        """
        input_str = "1234567890"
        
        # Serialize using BcsString
        serializer = Serializer()
        string_obj = BcsString(input_str)
        string_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_obj = BcsString.deserialize(deserializer)
        output_str = output_obj.value
        
        assert input_str == output_str
    
    def test_byte_ser_and_der(self):
        """
        Test U8/byte serialization and deserialization.
        Equivalent to C# ByteSerAndDerTest.
        """
        input_val = 15
        
        # Serialize
        serializer = Serializer()
        u8_obj = U8(input_val)
        u8_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_obj = U8.deserialize(deserializer)
        output_val = output_obj.value
        
        assert input_val == output_val
    
    def test_ushort_ser_and_der(self):
        """
        Test U16/ushort serialization and deserialization.
        Equivalent to C# UShortSerAndDerTest.
        """
        input_val = 11115  # From C# test: 111_15
        
        # Serialize
        serializer = Serializer()
        u16_obj = U16(input_val)
        u16_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_obj = U16.deserialize(deserializer)
        output_val = output_obj.value
        
        assert input_val == output_val
    
    def test_uint_ser_and_der(self):
        """
        Test U32/uint serialization and deserialization.
        Equivalent to C# UIntSerAndDerTest.
        """
        input_val = 1111111115  # From C# test: 1_111_111_115
        
        # Serialize
        serializer = Serializer()
        u32_obj = U32(input_val)
        u32_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_obj = U32.deserialize(deserializer)
        output_val = output_obj.value
        
        assert input_val == output_val
    
    def test_ulong_ser_and_der(self):
        """
        Test U64/ulong serialization and deserialization.
        Equivalent to C# ULongSerAndDerTest.
        """
        input_val = 1111111111111111115  # From C# test: 1_111_111_111_111_111_115
        
        # Serialize
        serializer = Serializer()
        u64_obj = U64(input_val)
        u64_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_obj = U64.deserialize(deserializer)
        output_val = output_obj.value
        
        assert input_val == output_val
    
    def test_uint128_big_integer_ser_and_der(self):
        """
        Test U128 with BigInteger serialization and deserialization.
        Equivalent to C# UInt128BigIntegerSerAndDerTest.
        """
        # From C# test: "1111111111111111111111111111111111115"
        input_val = int("1111111111111111111111111111111111115")
        
        # Serialize
        serializer = Serializer()
        u128_obj = U128(input_val)
        u128_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_obj = U128.deserialize(deserializer)
        output_val = output_obj.value
        
        assert input_val == output_val
    
    def test_uint256_big_integer_ser_and_der(self):
        """
        Test U256 with BigInteger serialization and deserialization.
        Equivalent to C# UInt256BigIntegerSerAndDerTest.
        """
        # From C# test: "111111111111111111111111111111111111111111111111111111111111111111111111111115"
        input_val = int("111111111111111111111111111111111111111111111111111111111111111111111111111115")
        
        # Serialize
        serializer = Serializer()
        u256_obj = U256(input_val)
        u256_obj.serialize(serializer)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize
        deserializer = Deserializer(serialized_data)
        output_obj = U256.deserialize(deserializer)
        output_val = output_obj.value
        
        assert input_val == output_val
    
    def test_uleb128_ser_and_der(self):
        """
        Test ULEB128 encoding/decoding.
        Equivalent to C# ULeb128SerAndDerTest.
        """
        input_val = 1111111115  # From C# test: 1_111_111_115
        
        # Serialize using ULEB128 encoding directly
        serializer = Serializer()
        serializer.write_uleb128(input_val)
        
        # Get serialized bytes
        serialized_data = serializer.to_bytes()
        
        # Deserialize using ULEB128 decoding
        deserializer = Deserializer(serialized_data)
        output_val = deserializer.read_uleb128()
        
        assert input_val == output_val
    
    def test_simple_programming_transactions(self):
        """
        Test simple programming transactions.
        Equivalent to C# SimpleProgrammingTransactionsTest.
        
        This is a complex test that validates MoveCall serialization
        with various argument types.
        """
        # Address constants from C# test
        sui = "0x0000000000000000000000000000000000000000000000000000000000000002"
        capy = "0x0000000000000000000000000000000000000000000000000000000000000006"
        
        sui_address = SuiAddress(sui)
        capy_address = SuiAddress(capy)
        
        # Create MoveCall transaction like C# test
        move_call = MoveCallCommand(
            package=sui,
            module="display",
            function="new",
            type_arguments=[f"{capy}::capy::Capy"],
            arguments=[
                GasCoinArgument(),                    # TransactionArgument(GasCoin, null)
                NestedResultArgument(0, 1),           # TransactionArgument(NestedResult, NestedResult(0, 1))
                InputArgument(3),                     # TransactionArgument(Input, TransactionBlockInput(3))
                ResultArgument(1)                     # TransactionArgument(Result, Result(1))
            ]
        )
        
        # Serialize the MoveCall
        serializer = Serializer()
        move_call.serialize(serializer)
        actual_bytes = serializer.to_bytes()
        
        # Expected bytes from C# test
        # expected_bytes = bytes([
        #     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
        #     7, 100, 105, 115, 112, 108, 97, 121,
        #     3, 110, 101, 119,
        #     1,
        #     7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6,
        #     4, 99, 97, 112, 121,
        #     4, 67, 97, 112, 121,
        #     0,
        #     4,
        #     0,
        #     3, 0, 0, 1, 0, 1,
        #     3, 0,
        #     2, 1, 0
        # ])
        expected_bytes = bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 7, 100, 105, 115, 112, 108, 97, 121, 3, 110, 101, 119, 1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 4, 99, 97, 112, 121, 4, 67, 97, 112, 121, 0, 4, 0, 3, 0, 0, 1, 0, 1, 3, 0, 2, 1, 0])
        
        # Compare serialized result
        print(f"Actual bytes length: {len(actual_bytes)}")
        print(f"Expected bytes length: {len(expected_bytes)}")
        print(f"Actual:   {actual_bytes.hex()}")
        print(f"Expected: {expected_bytes.hex()}")
        
        assert actual_bytes == expected_bytes, (
            f"ACTUAL LENGTH: {len(actual_bytes)}\n"
            f"EXPECTED LENGTH: {len(expected_bytes)}\n"
            f"Actual bytes:   {actual_bytes.hex()}\n"
            f"Expected bytes: {expected_bytes.hex()}"
        )


if __name__ == "__main__":
    pytest.main([__file__]) 