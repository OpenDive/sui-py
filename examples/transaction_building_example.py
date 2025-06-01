"""
Comprehensive example of the SuiPy transaction building system.

This example demonstrates:
- Basic transaction building with fluent API
- Various command types (Move calls, transfers, coin operations)
- Result chaining between commands
- BCS serialization and integration
"""

import asyncio
from sui_py.transactions import (
    TransactionBuilder, 
    ProgrammableTransactionBlock,
    ObjectArgument,
    PureArgument,
    ResultArgument
)
from sui_py.types import ObjectRef
from sui_py.bcs import Deserializer


def basic_transaction_example():
    """Basic transaction building example."""
    print("=== Basic Transaction Example ===")
    
    # Create a new transaction builder
    tx = TransactionBuilder()
    
    # Add pure value arguments
    amount = tx.pure(1000, "u64")
    recipient = tx.pure("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
    
    # Add object references (with version and digest as required)
    coin = tx.object(
        "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        version=1,
        digest="test_digest"
    )
    
    # Perform coin split
    new_coins = tx.split_coins(coin, [amount])
    
    # Transfer the new coin
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Build the PTB and serialize
    ptb = tx.build()
    print(f"PTB Summary:\n{ptb}")
    
    # Serialize to BCS bytes
    bcs_bytes = ptb.to_bytes()
    print(f"BCS bytes length: {len(bcs_bytes)}")
    print()


def complex_defi_transaction_example():
    """Complex DeFi transaction with multiple operations."""
    print("=== Complex DeFi Transaction Example ===")
    
    tx = TransactionBuilder()
    
    # Input parameters
    user_address = tx.pure("0x1111111111111111111111111111111111111111111111111111111111111111")
    pool_address = tx.object(
        "0x2222222222222222222222222222222222222222222222222222222222222222",
        version=10,
        digest="pool_digest"
    )
    liquidity_amount = tx.pure(5000, "u64")
    
    # Create gas coin and split for operations
    gas = tx.object(
        "0x3333333333333333333333333333333333333333333333333333333333333333",
        version=5,
        digest="gas_digest"
    )
    operation_coins = tx.split_coins(gas, [
        tx.pure(1000, "u64"), 
        tx.pure(2000, "u64"), 
        tx.pure(3000, "u64")
    ])
    
    # Provide liquidity to pool
    liquidity_result = tx.move_call(
        target="0x0000000000000000000000000000000000000000000000000000000000000003::pool::add_liquidity",
        arguments=[pool_address, operation_coins[0], liquidity_amount],
        type_arguments=[
            "0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI", 
            "0x0000000000000000000000000000000000000000000000000000000000000004::token::USDC"
        ]
    )
    
    # Stake LP tokens
    lp_tokens = liquidity_result[0]  # Get first result
    stake_result = tx.move_call(
        target="0x0000000000000000000000000000000000000000000000000000000000000005::staking::stake",
        arguments=[lp_tokens, operation_coins[1]],
        type_arguments=[
            "0x0000000000000000000000000000000000000000000000000000000000000003::pool::LP<0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI, 0x0000000000000000000000000000000000000000000000000000000000000004::token::USDC>"
        ]
    )
    
    # Transfer stake receipt to user
    stake_receipt = stake_result[0]
    tx.transfer_objects([stake_receipt], user_address)
    
    # Return remaining coins to user
    tx.transfer_objects([operation_coins[2]], user_address)
    
    print(f"Transaction Summary:\n{tx}")
    
    # Build and validate
    ptb = tx.build()
    print(f"Final PTB:\n{ptb}")
    print()


def move_call_example():
    """Demonstrate Move call patterns."""
    print("=== Move Call Example ===")
    
    tx = TransactionBuilder()
    
    # Create object inputs matching test patterns
    payment_obj = tx.object(
        "0x1000000000000000000000000000000000000000000000000000000000000000",
        version=10000,
        digest="1Bhh3pU9gLXZhoVxkr5wyg9sX6"
    )
    
    # Call a Move function (pattern from working tests)
    move_result = tx.move_call(
        target="0x0000000000000000000000000000000000000000000000000000000000000002::display::new",
        arguments=[payment_obj],
        type_arguments=["0x0000000000000000000000000000000000000000000000000000000000000002::capy::Capy"]
    )
    
    # Transfer the result
    recipient = tx.pure("0x0000000000000000000000000000000000000000000000000000000000000BAD")
    tx.transfer_objects([move_result[0]], recipient)
    
    # Build and serialize
    ptb = tx.build()
    serialized = ptb.to_bytes()
    
    print(f"Move call transaction built successfully")
    print(f"Serialized to {len(serialized)} bytes")
    print()


def result_chaining_example():
    """Demonstrate complex result chaining."""
    print("=== Result Chaining Example ===")
    
    tx = TransactionBuilder()
    
    # Create gas coin
    gas = tx.object(
        "0x4444444444444444444444444444444444444444444444444444444444444444",
        version=1,
        digest="gas_chain_digest"
    )
    
    # Create multiple amounts as pure arguments
    amounts = [
        tx.pure(100, "u64"), 
        tx.pure(200, "u64"), 
        tx.pure(300, "u64"), 
        tx.pure(400, "u64"), 
        tx.pure(500, "u64")
    ]
    
    # Split coins
    coins = tx.split_coins(gas, amounts)
    
    # Merge some coins together
    tx.merge_coins(coins[0], [coins[1], coins[2]])
    
    # Create recipients
    recipients = [
        tx.pure("0xrecipient1111111111111111111111111111111111111111111111111111111111"),
        tx.pure("0xrecipient2222222222222222222222222222222222222222222222222222222222")
    ]
    
    # Transfer coins to recipients
    tx.transfer_objects([coins[0]], recipients[0])
    tx.transfer_objects([coins[3]], recipients[1])
    tx.transfer_objects([coins[4]], recipients[0])
    
    print(f"Result chaining transaction:\n{tx}")
    
    # Build and serialize
    ptb = tx.build()
    print(f"Successfully built PTB with {len(ptb.commands)} commands")
    print()


def serialization_round_trip_example():
    """Demonstrate BCS serialization and deserialization."""
    print("=== Serialization Round Trip Example ===")
    
    # Create original transaction
    tx = TransactionBuilder()
    
    coin = tx.object(
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        version=1,
        digest="round_trip_digest"
    )
    amount = tx.pure(1000, "u64")
    recipient = tx.pure("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")
    
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Build and serialize
    original_ptb = tx.build()
    bcs_bytes = original_ptb.to_bytes()
    
    print(f"Original PTB:\n{original_ptb}")
    print(f"Serialized length: {len(bcs_bytes)} bytes")
    
    # Deserialize back
    deserializer = Deserializer(bcs_bytes)
    restored_ptb = ProgrammableTransactionBlock.deserialize(deserializer)
    
    print(f"Restored PTB:\n{restored_ptb}")
    
    # Verify they're equivalent
    original_bytes = original_ptb.to_bytes()
    restored_bytes = restored_ptb.to_bytes()
    
    print(f"Round trip successful: {original_bytes == restored_bytes}")
    print()


def error_handling_example():
    """Demonstrate error handling and validation."""
    print("=== Error Handling Example ===")
    
    try:
        # Invalid Move call target
        tx = TransactionBuilder()
        tx.move_call(target="invalid_target")  # Should fail
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    try:
        # Invalid object ID format
        tx = TransactionBuilder()
        tx.object("invalid_object_id")  # Should fail
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    try:
        # Empty transaction validation
        tx = TransactionBuilder()
        ptb = tx.build()  # May succeed but be empty
        if len(ptb.commands) == 0:
            print("Empty transaction created (no commands)")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    try:
        # Test invalid pure argument type
        tx = TransactionBuilder()
        tx.pure("not_a_valid_type", "invalid_type")  # Should fail during serialization
        ptb = tx.build()
        ptb.to_bytes()  # Failure might occur here
    except (ValueError, TypeError) as e:
        print(f"Caught expected error: {e}")
    
    print("Error handling working correctly!")
    print()


def integration_example():
    """Example showing transaction preparation for signing."""
    print("=== Integration Example ===")
    
    # Build transaction
    tx = TransactionBuilder()
    
    # Use realistic object IDs and operations
    coin = tx.object(
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        version=100,
        digest="integration_digest"
    )
    amount = tx.pure(1000000, "u64")  # 1 SUI (in MIST)
    recipient = tx.pure("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")
    
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Build and get transaction bytes for signing
    ptb = tx.build()
    ptb_bytes = ptb.to_bytes()
    
    print(f"Transaction ready for signing:")
    print(f"  PTB byte length: {len(ptb_bytes)}")
    print(f"  Number of commands: {len(ptb.commands)}")
    print(f"  Number of inputs: {len(ptb.inputs)}")
    print(f"  Transaction summary:\n{tx}")
    
    # In a real scenario, you would:
    # 1. Create complete TransactionData with gas, sender, etc.
    # 2. Sign the transaction with a private key
    # 3. Submit to Sui network for execution
    # 4. Wait for transaction confirmation
    
    print("Ready for integration with signing and network submission!")
    print()


def main():
    """Run all examples."""
    print("SuiPy Transaction Building System Examples")
    print("=" * 50)
    print()
    
    basic_transaction_example()
    complex_defi_transaction_example()
    move_call_example()
    result_chaining_example()
    serialization_round_trip_example()
    error_handling_example()
    integration_example()
    
    print("All examples completed successfully!")


if __name__ == "__main__":
    main() 