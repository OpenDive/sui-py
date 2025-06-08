"""
Comprehensive example of the SuiPy transaction building system.

This example demonstrates:
- Complete transaction building with metadata (NEW)
- Basic PTB building with fluent API
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
from sui_py.types import ObjectRef, SuiAddress
from sui_py.bcs import Deserializer


def complete_transaction_example():
    """Complete transaction building with metadata - NEW APPROACH."""
    print("=== Complete Transaction Example (NEW) ===")
    
    # Create a new transaction builder
    tx = TransactionBuilder()
    
    # Add pure value arguments
    amount = tx.pure(1000, "u64")
    recipient = tx.pure("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
    
    # Add object references (with version and digest as required)
    coin = tx.object(
        "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        version=1,
        digest="2w4Aj1eTq2yzN1VhN4GBKWfmhHAyuUApZ3MQoSiw6gki"
    )
    
    # Perform coin split
    new_coins = tx.split_coins(coin, [amount])
    
    # Transfer the new coin
    tx.transfer_objects([new_coins[0]], recipient)
    
    # NEW: Set transaction metadata (required for complete transactions)
    tx.set_sender("0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba")
    tx.set_gas_budget(1000000)  # 1 SUI worth of gas budget
    tx.set_gas_price(1000)      # Standard gas price
    
    # Gas payment objects (these would typically come from querying the network)
    gas_coin_ref = ObjectRef(
        object_id="0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        version=1,
        digest="3o5N7vH9wRdFy2KzE8LmQpXbGhCyaJmVz4TkPsAx1EqD"
    )
    tx.set_gas_payment([gas_coin_ref])
    
    # Optional: Set expiration
    tx.set_expiration_epoch(1000)
    
    # Build the complete transaction (NEW: returns TransactionData)
    transaction_data = tx.build_sync()
    print(f"Complete Transaction Summary:\n{tx}")
    print(f"Transaction Type: {type(transaction_data).__name__}")
    
    # Serialize complete transaction to BCS bytes
    bcs_bytes = transaction_data.to_bytes()
    print(f"Complete transaction BCS bytes length: {len(bcs_bytes)}")
    print()


def basic_ptb_example():
    """Basic PTB building example - LEGACY APPROACH."""
    print("=== Basic PTB Example (Legacy) ===")
    
    # Create a new transaction builder
    tx = TransactionBuilder()
    
    # Add pure value arguments
    amount = tx.pure(1000, "u64")
    recipient = tx.pure("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
    
    # Add object references (with version and digest as required)
    coin = tx.object(
        "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        version=1,
        digest="2w4Aj1eTq2yzN1VhN4GBKWfmhHAyuUApZ3MQoSiw6gki"
    )
    
    # Perform coin split
    new_coins = tx.split_coins(coin, [amount])
    
    # Transfer the new coin
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Build just the PTB (legacy approach)
    ptb = tx.build_ptb_sync()
    print(f"PTB Summary:\n{ptb}")
    
    # Serialize to BCS bytes
    bcs_bytes = ptb.to_bytes()
    print(f"PTB BCS bytes length: {len(bcs_bytes)}")
    print()


def complex_defi_transaction_example():
    """Complex DeFi transaction with complete metadata."""
    print("=== Complex DeFi Transaction Example ===")
    
    tx = TransactionBuilder()
    
    # Input parameters
    user_address = tx.pure("0x1111111111111111111111111111111111111111111111111111111111111111")
    pool_address = tx.object(
        "0x2222222222222222222222222222222222222222222222222222222222222222",
        version=10,
        digest="4p6O8xI2bSeFz3LaF9OnRqYcHjDzaKnWA5VlQtBy2FrE"
    )
    liquidity_amount = tx.pure(5000, "u64")
    
    # Create gas coin and split for operations
    gas = tx.object(
        "0x3333333333333333333333333333333333333333333333333333333333333333",
        version=5,
        digest="5q7P9yJ3cTfG A4McG1PoStZdIkEAaLoXB6WmRuCz3GsF"
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
    
    # Set complete transaction metadata
    tx.set_sender("0x1111111111111111111111111111111111111111111111111111111111111111")
    tx.set_gas_budget(5000000)  # Higher budget for complex DeFi operations
    tx.set_gas_price(1000)
    
    # Gas payment
    gas_payment = ObjectRef(
        object_id="0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        version=100,
        digest="6r8Q2zK4dUgHA5NdH2QpTuaeJlFBbMpYC7XnSvDz4HtG"
    )
    tx.set_gas_payment([gas_payment])
    
    print(f"Transaction Summary:\n{tx}")
    
    # Build complete transaction
    transaction_data = tx.build_sync()
    print(f"Complete DeFi transaction built successfully")
    print(f"Transaction has {len(transaction_data.transaction_data_v1.transaction_kind.programmable_transaction.commands)} commands")
    print()


def move_call_example():
    """Demonstrate Move call patterns with complete transaction."""
    print("=== Move Call Example ===")
    
    tx = TransactionBuilder()
    
    # Create object inputs matching test patterns
    payment_obj = tx.object(
        "0x1000000000000000000000000000000000000000000000000000000000000000",
        version=10000,
        digest="7s9R3AaL5eVhI B6OeI3RqVfZfJmGCcNqZD8YoTwEz5IuH"
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
    
    # Set transaction metadata
    tx.set_sender("0x0000000000000000000000000000000000000000000000000000000000000BAD")
    tx.set_gas_budget(2000000)
    tx.set_gas_price(1000)
    
    gas_ref = ObjectRef(
        object_id="0xcafebabecafebabecafebabecafebabecafebabecafebabecafebabecafebabe",
        version=42,
        digest="8t1S4BbM6fWiJC7PfJ4SrWgagKnHDdOraE9ZpUxF A6JvI"
    )
    tx.set_gas_payment([gas_ref])
    
    # Build and serialize complete transaction
    transaction_data = tx.build_sync()
    serialized = transaction_data.to_bytes()
    
    print(f"Move call transaction built successfully")
    print(f"Serialized to {len(serialized)} bytes")
    print()


async def async_transaction_example():
    """Demonstrate async transaction building with object resolution."""
    print("=== Async Transaction with Object Resolution ===")
    
    tx = TransactionBuilder()
    
    # Use unresolved objects (without version/digest)
    coin = tx.object("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
    amount = tx.pure(1000, "u64")
    recipient = tx.pure("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")
    
    # Perform operations with unresolved objects
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Set transaction metadata
    tx.set_sender("0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba")
    tx.set_gas_budget(1000000)
    tx.set_gas_price(1000)
    
    gas_ref = ObjectRef(
        object_id="0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
        version=1,
        digest="9u2T5CcN7gXjKD8QgK5TsXhbhLnIEePs bF1aqVyGA7KwJ"
    )
    tx.set_gas_payment([gas_ref])
    
    print(f"Transaction with unresolved objects:")
    print(f"  Unresolved objects: {len(tx._unresolved_objects)}")
    
    # In a real scenario, you would pass a SuiClient here:
    # transaction_data = await tx.build(client)
    
    # For demo purposes, show that it requires a client
    try:
        transaction_data = await tx.build()  # No client provided
    except ValueError as e:
        print(f"Expected error (no client): {e}")
    
    print("Async resolution would work with a real SuiClient")
    print()


def result_chaining_example():
    """Demonstrate complex result chaining with complete transaction."""
    print("=== Result Chaining Example ===")
    
    tx = TransactionBuilder()
    
    # Create gas coin
    gas = tx.object(
        "0x4444444444444444444444444444444444444444444444444444444444444444",
        version=1,
        digest="1Au3U6DdO8YkLE9RhL6UtYicIoJGFfQtcG2bsWzHB8LvK"
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
    
    # Set complete transaction metadata
    tx.set_sender("0x4444444444444444444444444444444444444444444444444444444444444444")
    tx.set_gas_budget(2000000)
    tx.set_gas_price(1000)
    
    gas_payment = ObjectRef(
        object_id="0x5555555555555555555555555555555555555555555555555555555555555555",
        version=10,
        digest="2Bv4V7EeP9ZlMF1SiM7VuZjdJpKHGgRudH3ctXyIC9MwL"
    )
    tx.set_gas_payment([gas_payment])
    
    print(f"Result chaining transaction:\n{tx}")
    
    # Build complete transaction
    transaction_data = tx.build_sync()
    print(f"Successfully built complete transaction with {len(transaction_data.transaction_data_v1.transaction_kind.programmable_transaction.commands)} commands")
    print()


def serialization_round_trip_example():
    """Demonstrate BCS serialization and deserialization."""
    print("=== Serialization Round Trip Example ===")
    
    # Create original transaction
    tx = TransactionBuilder()
    
    coin = tx.object(
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        version=1,
        digest="3Cw5W8FfQ1AmNG2TjN8WvAkeMqLIHhSvuI4duYzJD1NxM"
    )
    amount = tx.pure(1000, "u64")
    recipient = tx.pure("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")
    
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Set transaction metadata
    tx.set_sender("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")
    tx.set_gas_budget(1000000)
    tx.set_gas_price(1000)
    
    gas_ref = ObjectRef(
        object_id="0x6666666666666666666666666666666666666666666666666666666666666666",
        version=5,
        digest="4Dx6X9GgR2BnOH3UkO9XwBlf NrMJIiTwvJ5evZzKE2OyN"
    )
    tx.set_gas_payment([gas_ref])
    
    # Build and serialize complete transaction
    original_transaction = tx.build_sync()
    bcs_bytes = original_transaction.to_bytes()
    
    print(f"Original Transaction built successfully")
    print(f"Serialized length: {len(bcs_bytes)} bytes")
    
    # For PTB-only round trip (legacy)
    ptb = tx.build_ptb_sync()
    ptb_bytes = ptb.to_bytes()
    
    # Deserialize PTB back
    deserializer = Deserializer(ptb_bytes)
    restored_ptb = ProgrammableTransactionBlock.deserialize(deserializer)
    
    print(f"PTB round trip successful: {ptb_bytes == restored_ptb.to_bytes()}")
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
        # Missing transaction metadata
        tx = TransactionBuilder()
        tx.transfer_objects([tx.object("0x123", version=1, digest="5Ey7Y1HhS3CoPI4VlP1YxCmgOs")], tx.pure("0x456"))
        transaction_data = tx.build_sync()  # Should fail due to missing metadata
    except ValueError as e:
        print(f"Caught expected error (missing metadata): {e}")
    
    try:
        # Empty transaction validation
        tx = TransactionBuilder()
        tx.set_sender("0x123")
        tx.set_gas_budget(1000000)
        tx.set_gas_price(1000)
        tx.set_gas_payment([ObjectRef("0x456", 1, "6Fz8Z2IiT4DpQJ5WmQ2ZyDnhPt")])
        transaction_data = tx.build_sync()  # Should fail due to no commands
    except ValueError as e:
        print(f"Caught expected error (empty transaction): {e}")
    
    print("Error handling working correctly!")
    print()


def integration_example():
    """Example showing complete transaction preparation for signing."""
    print("=== Integration Example ===")
    
    # Build transaction
    tx = TransactionBuilder()
    
    # Use realistic object IDs and operations
    coin = tx.object(
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        version=100,
        digest="7G A1A3JjU5EqRK6XnR3ZzEohQu"
    )
    amount = tx.pure(1000000, "u64")  # 1 SUI (in MIST)
    recipient = tx.pure("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")
    
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Set complete transaction metadata
    sender = "0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba"
    tx.set_sender(sender)
    tx.set_gas_budget(1000000)
    tx.set_gas_price(1000)
    
    gas_payment = ObjectRef(
        object_id="0x7777777777777777777777777777777777777777777777777777777777777777",
        version=50,
        digest="8H1B2B4KkV6FrSL7YoS4A1FpiRv"
    )
    tx.set_gas_payment([gas_payment])
    
    # Build complete transaction ready for signing
    transaction_data = tx.build_sync()
    transaction_bytes = transaction_data.to_bytes()
    
    print(f"Complete transaction ready for signing:")
    print(f"  Transaction byte length: {len(transaction_bytes)}")
    print(f"  Sender: {transaction_data.transaction_data_v1.sender}")
    print(f"  Gas budget: {transaction_data.transaction_data_v1.gas_data.budget}")
    print(f"  Gas price: {transaction_data.transaction_data_v1.gas_data.price}")
    print(f"  Number of commands: {len(transaction_data.transaction_data_v1.transaction_kind.programmable_transaction.commands)}")
    print(f"  Number of inputs: {len(transaction_data.transaction_data_v1.transaction_kind.programmable_transaction.inputs)}")
    print(f"  Transaction summary:\n{tx}")
    
    # In a real scenario, you would:
    # 1. Sign the transaction_bytes with a private key
    # 2. Submit the signed transaction to Sui network
    # 3. Wait for transaction confirmation and effects
    
    print("Ready for signing and network submission!")
    print()


async def main():
    """Run all examples."""
    print("SuiPy Transaction Building System Examples")
    print("=" * 50)
    print()
    
    complete_transaction_example()  # NEW: Complete transaction building
    basic_ptb_example()             # Legacy PTB-only building
    complex_defi_transaction_example()
    move_call_example()
    await async_transaction_example()  # NEW: Async object resolution
    result_chaining_example()
    serialization_round_trip_example()
    error_handling_example()
    integration_example()
    
    print("All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main()) 