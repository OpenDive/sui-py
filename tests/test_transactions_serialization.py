#!/usr/bin/env python3
"""
Direct serialization tests equivalent to C# TransactionsTest.cs

These tests bypass TransactionBuilder and create data structures directly
to test serialization correctness at the low level, just like the C# tests.
"""

import pytest
from sui_py.transactions.ptb import ProgrammableTransactionBlock
from sui_py.transactions.commands import MoveCall, Command
from sui_py.transactions.transaction_argument import ObjectArgument
from sui_py.transactions.data import TransactionDataV1, TransactionData, TransactionKind
from sui_py.transactions.gas import GasData
from sui_py.transactions.expiration import TransactionExpiration
from sui_py.types import ObjectRef, SuiAddress, StructTypeTag
from sui_py.bcs import serialize


class TestTransactionsSerialization:
    """Low-level serialization tests equivalent to C# TransactionsTest.cs"""
    
    def setup_method(self):
        """Setup test data matching C# test exactly"""
        self.test_address = "0x0000000000000000000000000000000000000000000000000000000000000BAD"
        self.object_id = "0x1000000000000000000000000000000000000000000000000000000000000000"
        self.version = 10000
        self.digest = "1Bhh3pU9gLXZhoVxkr5wyg9sX6"
        self.sui_address_hex = "0x0000000000000000000000000000000000000000000000000000000000000002"

    def test_transaction_data_serialization_single_input(self):
        """
        Test equivalent to C# TransactionDataSerializationSingleInput
        Creates transaction with single input directly (no TransactionBuilder)
        """
        # Create ObjectRef directly (equivalent to SuiObjectRef in C#)
        object_ref = ObjectRef(
            object_id=self.object_id,
            version=self.version,
            digest=self.digest
        )
        
        # Create ObjectArgument with explicit ImmOrOwned type (variant 0)
        # This matches: new ObjectArg(ObjectRefType.ImmOrOwned, paymentRef)
        object_argument = ObjectArgument(object_ref)
        
        # Create PTB inputs directly (equivalent to CallArg[] inputs in C#)
        ptb_inputs = [object_argument]
        
        # Create MoveCall directly
        # Equivalent to: new MoveCall(target, type_arguments, arguments)
        move_call = MoveCall(
            package=SuiAddress.from_hex(self.sui_address_hex),
            module="display",
            function="new",
            type_arguments=[
                StructTypeTag(
                    package=SuiAddress.from_hex(self.sui_address_hex),
                    module="capy", 
                    name="Capy",
                    type_params=[]
                )
            ],
            arguments=[0]  # Single argument referencing input 0
        )
        
        # Create Command directly
        command = Command(move_call)
        
        # Create PTB directly (equivalent to ProgrammableTransaction in C#)
        ptb = ProgrammableTransactionBlock(
            inputs=ptb_inputs,
            commands=[command]
        )
        
        # Create TransactionKind
        transaction_kind = TransactionKind(ptb)
        
        # Create GasData
        gas_data = GasData(
            budget=1000000,
            price=1,
            payment=[object_ref],
            owner=SuiAddress.from_hex(self.sui_address_hex)
        )
        
        # Create TransactionDataV1 directly
        transaction_data_v1 = TransactionDataV1(
            sender=SuiAddress.from_hex(self.test_address),
            expiration=TransactionExpiration(),
            gas_data=gas_data,
            transaction_kind=transaction_kind
        )
        
        # Create TransactionData
        transaction_data = TransactionData(transaction_data_v1)
        
        # Serialize and get bytes
        actual = serialize(transaction_data)
        
        # Expected bytes from C# test
        expected = bytes([
            0, 0, 1, 1, 0, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 39, 0, 0, 0, 0, 0, 0, 20, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 7, 100, 105, 115, 112, 108, 97, 121, 3, 110, 101, 119, 1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4, 99, 97, 112, 121, 4, 67, 97, 112, 121, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 173, 1, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 39, 0, 0, 0, 0, 0, 0, 20, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 64, 66, 15, 0, 0, 0, 0, 0, 0
        ])
        
        print(f"Actual length: {len(actual)}")
        print(f"Expected length: {len(expected)}")
        print(f"Actual bytes: {actual.hex()}")
        print(f"Expected bytes: {expected.hex()}")
        
        # Find first difference for debugging
        if actual != expected:
            for i, (a, e) in enumerate(zip(actual, expected)):
                if a != e:
                    print(f"First difference at position {i}: actual=0x{a:02x}, expected=0x{e:02x}")
                    break
        
        assert actual == expected, f"Serialization mismatch"

    def test_transaction_data_serialization_multiple_args(self):
        """
        Test equivalent to C# TransactionDataSerialization
        Creates transaction with multiple arguments directly (no TransactionBuilder)
        """
        # Create ObjectRef directly
        object_ref = ObjectRef(
            object_id=self.object_id,
            version=self.version,
            digest=self.digest
        )
        
        # Create ObjectArgument with explicit ImmOrOwned type (variant 0)
        object_argument = ObjectArgument(object_ref)
        
        # Create PTB inputs directly
        ptb_inputs = [object_argument]
        
        # Create MoveCall with multiple arguments
        # Equivalent to C# test with 3 arguments: Input(0), Input(1), Result(2)
        move_call = MoveCall(
            package=SuiAddress.from_hex(self.sui_address_hex),
            module="display",
            function="new",
            type_arguments=[
                StructTypeTag(
                    package=SuiAddress.from_hex(self.sui_address_hex),
                    module="capy",
                    name="Capy", 
                    type_params=[]
                )
            ],
            arguments=[0, 1, (2, 0)]  # Input(0), Input(1), Result(2, 0)
        )
        
        # Create Command directly
        command = Command(move_call)
        
        # Create PTB directly
        ptb = ProgrammableTransactionBlock(
            inputs=ptb_inputs,
            commands=[command]
        )
        
        # Create TransactionKind
        transaction_kind = TransactionKind(ptb)
        
        # Create GasData
        gas_data = GasData(
            budget=1000000,
            price=1,
            payment=[object_ref],
            owner=SuiAddress.from_hex(self.sui_address_hex)
        )
        
        # Create TransactionDataV1 directly
        transaction_data_v1 = TransactionDataV1(
            sender=SuiAddress.from_hex(self.test_address),
            expiration=TransactionExpiration(),
            gas_data=gas_data,
            transaction_kind=transaction_kind
        )
        
        # Create TransactionData
        transaction_data = TransactionData(transaction_data_v1)
        
        # Serialize and get bytes
        actual = serialize(transaction_data)
        
        # Expected bytes from C# test (TransactionDataSerialization)
        expected = bytes([
            0, 0, 1, 1, 0, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 39, 0, 0, 0, 0, 0, 0, 20, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 7, 100, 105, 115, 112, 108, 97, 121, 3, 110, 101, 119, 1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4, 99, 97, 112, 121, 4, 67, 97, 112, 121, 0, 3, 1, 0, 0, 1, 1, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 173, 1, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 39, 0, 0, 0, 0, 0, 0, 20, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 64, 66, 15, 0, 0, 0, 0, 0, 0
        ])
        
        print(f"Actual length: {len(actual)}")
        print(f"Expected length: {len(expected)}")
        print(f"Actual bytes: {actual.hex()}")
        print(f"Expected bytes: {expected.hex()}")
        
        # Find first difference for debugging
        if actual != expected:
            for i, (a, e) in enumerate(zip(actual, expected)):
                if a != e:
                    print(f"First difference at position {i}: actual=0x{a:02x}, expected=0x{e:02x}")
                    break
        
        assert actual == expected, f"Serialization mismatch" 