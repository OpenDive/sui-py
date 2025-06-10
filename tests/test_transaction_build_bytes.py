"""
Test transaction build bytes against TypeScript SDK output.

This module tests that the Python SDK produces identical transaction bytes
to the TypeScript SDK for various transaction scenarios.
"""

import pytest
from sui_py.transactions import TransactionBuilder
from sui_py.types import ObjectRef


def ref():
    """Create a test ObjectRef with known values (matches TypeScript SDK tests)."""
    return ObjectRef(
        object_id="0x5877400000000000000000000000000000000000000000000000000000000000",
        version=3619,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
    )


def setup():
    """Create a standard TransactionBuilder configuration (matches TypeScript SDK tests)."""
    tx = TransactionBuilder()
    tx.set_sender('0x2')
    tx.set_gas_price(5)
    tx.set_gas_budget(100)
    tx.set_gas_payment([ref()])
    return tx


def assert_bytes_match(actual_bytes, expected_bytes, test_name):
    """
    Compare byte arrays with detailed error reporting.
    
    Args:
        actual_bytes: List of integers from Python SDK
        expected_bytes: List of integers from TypeScript SDK
        test_name: Name of the test for error reporting
    """
    if actual_bytes == expected_bytes:
        print(f"✅ {test_name}: Byte arrays match perfectly!")
        return
    
    print(f"❌ {test_name}: Byte arrays do not match")
    print(f"   Python length: {len(actual_bytes)}")
    print(f"   TypeScript length: {len(expected_bytes)}")
    
    # Find first difference
    min_length = min(len(actual_bytes), len(expected_bytes))
    for i in range(min_length):
        if actual_bytes[i] != expected_bytes[i]:
            print(f"   First difference at index {i}:")
            print(f"     Python: {actual_bytes[i]}")
            print(f"     TypeScript: {expected_bytes[i]}")
            break
    
    # Show context around the difference
    if min_length > 0:
        start = max(0, i - 5)
        end = min(min_length, i + 6)
        print(f"   Context (indices {start}-{end-1}):")
        print(f"     Python:     {actual_bytes[start:end]}")
        print(f"     TypeScript: {expected_bytes[start:end]}")
    
    # If lengths differ, show the extra bytes
    if len(actual_bytes) != len(expected_bytes):
        if len(actual_bytes) > len(expected_bytes):
            print(f"   Extra Python bytes: {actual_bytes[len(expected_bytes):]}")
        else:
            print(f"   Extra TypeScript bytes: {expected_bytes[len(actual_bytes):]}")
    
    assert actual_bytes == expected_bytes, f"{test_name} byte arrays do not match"


class TestTransactionBuildBytes:
    """Test transaction serialization against TypeScript SDK output."""
    
    @pytest.mark.asyncio
    async def test_empty_transaction_offline(self):
        """Test that empty transaction produces expected bytes."""
        tx = setup()
        transaction_data = await tx.build()
        actual_bytes = list(transaction_data.to_bytes())
        
        # Placeholder - replace with TypeScript SDK output
        # From: tx = setup(); await tx.build();
        expected_bytes = [
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,5,0,0,0,0,0,0,0,100,0,0,0,0,0,0,0,0
        ]
        
        assert_bytes_match(actual_bytes, expected_bytes, "empty transaction")
    
    @pytest.mark.asyncio
    async def test_epoch_expiration(self):
        """Test transaction with epoch expiration."""
        tx = setup()
        tx.set_expiration_epoch(1)
        transaction_data = await tx.build()
        actual_bytes = list(transaction_data.to_bytes())
        
        # Placeholder - replace with TypeScript SDK output
        # From: tx = setup(); tx.setExpiration({ Epoch: 1 }); await tx.build();
        expected_bytes = [
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,5,0,0,0,0,0,0,0,100,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0
        ]
        
        assert_bytes_match(actual_bytes, expected_bytes, "epoch expiration")
    
    @pytest.mark.asyncio
    async def test_split_coins_transaction(self):
        """Test simple split coins transaction."""
        tx = setup()
        
        tx.split_coins(
            tx.gas_coin(),          # Coin to split
            [tx.pure(100, "u64")]   # Amounts for new coins
        )
        
        transaction_data = await tx.build()
        
        print(f"JSON: {tx.to_json()}")
        
        actual_bytes = list(transaction_data.to_bytes())
        
        # Placeholder - replace with TypeScript SDK output
        # From: tx = setup(); tx.add(Commands.SplitCoins(tx.gas, [tx.pure.u64(100)])); await tx.build();
        expected_bytes = [
            0,0,1,0,8,100,0,0,0,0,0,0,0,1,2,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,5,0,0,0,0,0,0,0,100,0,0,0,0,0,0,0,0
        ]
        
        assert_bytes_match(actual_bytes, expected_bytes, "split coins")

    @pytest.mark.asyncio
    async def test_pre_serialized_inputs(self):
        """Test transaction with pre-serialized inputs as bytes."""
        tx = setup()
        
        # Serialize u64 value directly as bytes (equivalent to bcs.U64.serialize(100n).toBytes())
        from sui_py.bcs import serialize, U64
        input_bytes = serialize(U64(100))
        
        # Use bytes directly as pre-serialized BCS data (TypeScript compatibility)
        tx.split_coins(tx.gas_coin(), [tx.pure(input_bytes, "bcs")])
        transaction_data = await tx.build()
        actual_bytes = list(transaction_data.to_bytes())
        
        # Placeholder - replace with TypeScript SDK output
        # From: tx = setup(); inputBytes = bcs.U64.serialize(100n).toBytes(); 
        #       tx.add(Commands.SplitCoins(tx.gas, [tx.pure(inputBytes)])); await tx.build();
        expected_bytes = [
            0,0,1,0,8,100,0,0,0,0,0,0,0,1,2,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,5,0,0,0,0,0,0,0,100,0,0,0,0,0,0,0,0
        ]
        
        assert_bytes_match(actual_bytes, expected_bytes, "pre-serialized inputs")
    
    @pytest.mark.asyncio
    async def test_complex_interaction(self):
        """Test complex multi-command transaction."""
        tx = setup()
        
        # Split coins
        coin = tx.split_coins(tx.gas_coin(), [tx.pure(100, "u64")])
        
        # Merge coins
        tx.merge_coins(tx.gas_coin(), [coin.single(), tx.object(ref().object_id, ref().version, ref().digest)])
        
        # Move call
        tx.move_call(
            "0x2::devnet_nft::mint",
            arguments=[tx.pure("foo", "string"), tx.pure("bar", "string"), tx.pure("baz", "string")],
            type_arguments=[]
        )
        
        transaction_data = await tx.build()
        actual_bytes = list(transaction_data.to_bytes())
        
        # Placeholder - replace with TypeScript SDK output
        # From: complex interaction test in TypeScript
        expected_bytes = [
            0,0,5,0,8,100,0,0,0,0,0,0,0,1,0,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,4,3,102,111,111,0,4,3,98,97,114,0,4,3,98,97,122,3,2,0,1,1,0,0,3,0,2,2,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,10,100,101,118,110,101,116,95,110,102,116,4,109,105,110,116,0,3,1,2,0,1,3,0,1,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,5,0,0,0,0,0,0,0,100,0,0,0,0,0,0,0,0
        ]
        
        assert_bytes_match(actual_bytes, expected_bytes, "complex interaction")
    
    @pytest.mark.asyncio
    async def test_object_inputs(self):
        """Test transaction with object inputs."""
        tx = setup()
        
        # Add object input
        obj_input = tx.object(ref().object_id, ref().version, ref().digest)
        
        # Split coins
        coin = tx.split_coins(tx.gas_coin(), [tx.pure(100, "u64")])
        
        # Merge with object
        tx.merge_coins(tx.gas_coin(), [coin.single(), tx.object(ref().object_id, ref().version, ref().digest)])
        
        transaction_data = await tx.build()
        actual_bytes = list(transaction_data.to_bytes())
        
        expected_bytes = [
            # TODO: Replace with actual TypeScript SDK output  
            0,0,2,1,0,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,8,100,0,0,0,0,0,0,0,2,2,0,1,1,1,0,3,0,2,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,5,0,0,0,0,0,0,0,100,0,0,0,0,0,0,0,0
        ]
        
        assert_bytes_match(actual_bytes, expected_bytes, "object inputs")
    
    @pytest.mark.asyncio
    async def test_uses_receiving_argument(self):
        """Test transaction with receiving arguments (matches TypeScript)."""
        tx = setup()
        
        # Add regular object reference
        tx.object(ref().object_id, ref().version, ref().digest)
        
        # Split coins
        coin = tx.split_coins(tx.gas_coin(), [tx.pure(100, "u64")])
        
        # Merge coins with another object
        tx.merge_coins(tx.gas_coin(), [
            coin.single(),
            tx.object(ref().object_id, ref().version, ref().digest)
        ])
        
        # Move call with receiving argument
        tx.move_call(
            "0x2::devnet_nft::mint",
            arguments=[
                tx.object(ref().object_id, ref().version, ref().digest),     # Regular object
                tx.receiving_ref(ref().object_id, ref().version, ref().digest) # Receiving object
            ],
            type_arguments=[]
        )
        
        # Build and get bytes
        transaction_data = await tx.build()
        actual_bytes = list(transaction_data.to_bytes())
        
        # # Round-trip test
        # tx2 = TransactionBuilder.from_bytes(bytes1)
        # bytes2 = await tx2.to_bytes()
        
        # # Verify round-trip works
        # assert bytes1 == bytes2, "Round-trip serialization must be identical"
        
        # Compare with expected TypeScript output
        
        
        expected_bytes = [
            # TODO: Replace with actual TypeScript SDK output from:
            # tx = setup(); 
            # tx.object(Inputs.ObjectRef(ref()));
            # const coin = tx.splitCoins(tx.gas, [100]);
            # tx.add(Commands.MergeCoins(tx.gas, [coin, tx.object(Inputs.ObjectRef(ref()))]));
            # tx.add(Commands.MoveCall({
            #   target: '0x2::devnet_nft::mint',
            #   arguments: [tx.object(Inputs.ObjectRef(ref())), tx.object(Inputs.ReceivingRef(ref()))]
            # }));
            # const bytes = await tx.build();
            0,0,2,1,0,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,8,100,0,0,0,0,0,0,0,3,2,0,1,1,1,0,3,0,2,2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,10,100,101,118,110,101,116,95,110,102,116,4,109,105,110,116,0,2,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,5,0,0,0,0,0,0,0,100,0,0,0,0,0,0,0,0
        ]
        
        # For now, just validate structure
        print(f"Receiving argument test bytes length: {len(actual_bytes)}")
        print(f"First 20 bytes: {actual_bytes[:20]}")
        
        assert_bytes_match(actual_bytes, expected_bytes, "uses receiving argument")
        
    # @pytest.mark.asyncio
    # async def test_move_call_with_type_arguments(self):
    #     """Test move call with type arguments."""
    #     tx = setup()
        
    #     tx.move_call(
    #         "0x0000000000000000000000000000000000000000000000000000000000000002::coin::split",
    #         arguments=[tx.gas_coin(), tx.pure(100, "u64")],
    #         type_arguments=["0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI"]
    #     )
        
    #     transaction_data = await tx.build()
    #     actual_bytes = list(transaction_data.to_bytes())
        
    #     # Placeholder - replace with TypeScript SDK output
    #     expected_bytes = [
    #         # TODO: Replace with actual TypeScript SDK output
    #         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #         # ... add complete byte array from TypeScript test
    #     ]
        
    #     assert_bytes_match(actual_bytes, expected_bytes, "move call with type arguments")


# Utility function for manual testing
def print_transaction_bytes(transaction_data, test_name="transaction"):
    """
    Print transaction bytes in various formats for easy copying.
    
    Args:
        transaction_data: TransactionData object
        test_name: Name for the output
    """
    bytes_data = transaction_data.to_bytes()
    byte_array = list(bytes_data)
    
    print(f"\n=== {test_name} Bytes ===")
    print(f"Length: {len(byte_array)}")
    print(f"Python list: {byte_array}")
    print(f"Comma separated: {','.join(map(str, byte_array))}")
    print(f"Hex: {bytes_data.hex()}")


if __name__ == "__main__":
    """Run manual tests to generate byte arrays for comparison."""
    import asyncio
    
    async def generate_test_bytes():
        """Generate bytes for each test case to compare with TypeScript."""
        
        print("Generating transaction bytes for TypeScript comparison...")
        
        # Empty transaction
        tx = setup()
        transaction_data = await tx.build()
        print_transaction_bytes(transaction_data, "empty transaction")
        
        # Epoch expiration
        tx = setup()
        tx.set_expiration_epoch(1)
        transaction_data = await tx.build()
        print_transaction_bytes(transaction_data, "epoch expiration")
        
        # Split coins
        tx = setup()
        tx.split_coins(tx.gas_coin(), [tx.pure(100, "u64")])
        transaction_data = await tx.build()
        print_transaction_bytes(transaction_data, "split coins")
        
        print("\nUse these byte arrays to update the expected_bytes in the test cases!")
    
    asyncio.run(generate_test_bytes()) 