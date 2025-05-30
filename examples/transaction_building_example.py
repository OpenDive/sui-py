"""
Comprehensive example of the SuiPy transaction building system.

This example demonstrates:
- Basic transaction building with fluent API
- Various command types (Move calls, transfers, coin operations)
- Result chaining between commands
- Package publishing and upgrading
- BCS serialization and integration
"""

import asyncio
from sui_py import (
    TransactionBuilder, 
    SuiClient,
    ProgrammableTransactionBlock,
    PureArgument,
    ObjectArgument,
    ResultArgument
)


def basic_transaction_example():
    """Basic transaction building example."""
    print("=== Basic Transaction Example ===")
    
    # Create a new transaction builder
    tx = TransactionBuilder()
    
    # Add pure value arguments
    amount = tx.pure(1000, "u64")
    recipient = tx.pure("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
    
    # Add object references
    coin = tx.object("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
    
    # Perform coin split
    new_coins = tx.split_coins(coin, [amount])
    
    # Transfer the new coin
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Build the PTB
    ptb = tx.build()
    print(f"PTB Summary:\n{ptb}")
    
    # Serialize to BCS bytes
    bcs_bytes = tx.to_bytes()
    print(f"BCS bytes length: {len(bcs_bytes)}")
    print()


def complex_defi_transaction_example():
    """Complex DeFi transaction with multiple operations."""
    print("=== Complex DeFi Transaction Example ===")
    
    tx = TransactionBuilder()
    
    # Input parameters
    user_address = tx.pure("0x1111111111111111111111111111111111111111111111111111111111111111")
    pool_address = tx.object("0x2222222222222222222222222222222222222222222222222222222222222222")
    liquidity_amount = tx.pure(5000, "u64")
    
    # Split gas coin for operations
    gas = tx.gas_coin()
    operation_coins = tx.split_coins(gas, [1000, 2000, 3000])
    
    # Provide liquidity to pool
    liquidity_result = tx.move_call(
        "0x0000000000000000000000000000000000000000000000000000000000000003::pool::add_liquidity",
        arguments=[pool_address, operation_coins[0], liquidity_amount],
        type_arguments=["0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI", "0x0000000000000000000000000000000000000000000000000000000000000004::token::USDC"]
    )
    
    # Stake LP tokens
    lp_tokens = liquidity_result.single()
    stake_result = tx.move_call(
        "0x0000000000000000000000000000000000000000000000000000000000000005::staking::stake",
        arguments=[lp_tokens, operation_coins[1]],
        type_arguments=["0x0000000000000000000000000000000000000000000000000000000000000003::pool::LP<0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI, 0x0000000000000000000000000000000000000000000000000000000000000004::token::USDC>"]
    )
    
    # Transfer stake receipt to user
    stake_receipt = stake_result.single()
    tx.transfer_objects([stake_receipt], user_address)
    
    # Return remaining coins to user
    tx.transfer_objects([operation_coins[2]], user_address)
    
    print(f"Transaction Summary:\n{tx}")
    
    # Build and validate
    ptb = tx.build()
    print(f"Final PTB:\n{ptb}")
    print()


def package_management_example():
    """Package publishing and upgrading example."""
    print("=== Package Management Example ===")
    
    tx = TransactionBuilder()
    
    # Mock compiled module bytecode
    module1_bytecode = b"module_bytecode_1"
    module2_bytecode = b"module_bytecode_2"
    modules = [module1_bytecode, module2_bytecode]
    
    # Dependencies (framework packages)
    dependencies = ["0x0000000000000000000000000000000000000000000000000000000000000001", "0x0000000000000000000000000000000000000000000000000000000000000002"]
    
    # Publish package
    upgrade_cap = tx.publish(modules, dependencies)
    
    # Transfer upgrade capability to deployer
    deployer = tx.pure("0xdeployer1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
    tx.transfer_objects([upgrade_cap.single()], deployer)
    
    print(f"Package publish transaction:\n{tx}")
    
    # Build separate upgrade transaction
    upgrade_tx = TransactionBuilder()
    
    # New module bytecode for upgrade
    upgraded_modules = [b"upgraded_module_1", b"upgraded_module_2"]
    package_id = "0xabc1234567890abcdef1234567890abcdef1234567890abcdef1234567890abc"
    upgrade_cap_obj = upgrade_tx.object("0xdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")
    
    # Create upgrade ticket
    ticket = upgrade_tx.move_call(
        "0x0000000000000000000000000000000000000000000000000000000000000002::package::authorize_upgrade",
        arguments=[upgrade_cap_obj, upgrade_tx.pure(1, "u8"), upgrade_tx.pure(b"digest", "vector<u8>")]
    )
    
    # Perform upgrade
    receipt = upgrade_tx.upgrade(
        modules=upgraded_modules,
        dependencies=dependencies,
        package=package_id,
        ticket=ticket.single()
    )
    
    # Commit upgrade
    upgrade_tx.move_call(
        "0x0000000000000000000000000000000000000000000000000000000000000002::package::commit_upgrade",
        arguments=[upgrade_cap_obj, receipt.single()]
    )
    
    print(f"Package upgrade transaction:\n{upgrade_tx}")
    print()


def result_chaining_example():
    """Demonstrate complex result chaining."""
    print("=== Result Chaining Example ===")
    
    tx = TransactionBuilder()
    
    # Create multiple coins from gas
    gas = tx.gas_coin()
    amounts = [tx.pure(amount) for amount in [100, 200, 300, 400, 500]]
    coins = tx.split_coins(gas, amounts)
    
    # Merge some coins together
    tx.merge_coins(coins[0], [coins[1], coins[2]])
    
    # Create a vector of remaining coins
    coin_vector = tx.make_move_vec(
        [coins[3], coins[4]], 
        "0x0000000000000000000000000000000000000000000000000000000000000002::coin::Coin<0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI>"
    )
    
    # Use the vector in a batch transfer
    recipients = [
        tx.pure("0xrecipient1111111111111111111111111111111111111111111111111111111111"),
        tx.pure("0xrecipient2222222222222222222222222222222222222222222222222222222222")
    ]
    
    # Call batch transfer function with the coin vector
    tx.move_call(
        "0x0000000000000000000000000000000000000000000000000000000000000006::batch::transfer_coins",
        arguments=[coin_vector.single(), recipients[0], recipients[1]]
    )
    
    # Transfer the merged coin to first recipient
    tx.transfer_objects([coins[0]], recipients[0])
    
    print(f"Result chaining transaction:\n{tx}")
    print()


def serialization_round_trip_example():
    """Demonstrate BCS serialization and deserialization."""
    print("=== Serialization Round Trip Example ===")
    
    # Create original transaction
    tx = TransactionBuilder()
    
    coin = tx.object("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
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
    from sui_py.bcs import Deserializer
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
        tx.move_call("invalid_target")  # Should fail
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    try:
        # Invalid object ID
        tx = TransactionBuilder()
        tx.object("invalid_object_id")  # Should fail
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    try:
        # Empty transaction
        tx = TransactionBuilder()
        tx.build()  # Should fail - no commands
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    try:
        # Invalid result reference
        tx = TransactionBuilder()
        coin = tx.object("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        # This would create a forward reference, caught during PTB validation
        invalid_result = ResultArgument(999, 0)  # Non-existent command
        tx.transfer_objects([coin], invalid_result)
        ptb = tx.build()
        ptb.validate()  # Should fail
    except (ValueError, IndexError) as e:
        print(f"Caught expected error: {e}")
    
    print("Error handling working correctly!")
    print()


async def integration_example():
    """Example showing integration with SuiClient (mock)."""
    print("=== Integration Example ===")
    
    # Build transaction
    tx = TransactionBuilder()
    
    # Simulate real object IDs and operations
    coin = tx.object("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
    amount = tx.pure(1000000, "u64")  # 1 SUI (in MIST)
    recipient = tx.pure("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")
    
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Get transaction bytes for signing
    ptb_bytes = tx.to_bytes()
    
    print(f"Transaction ready for signing:")
    print(f"  PTB byte length: {len(ptb_bytes)}")
    print(f"  Transaction summary:\n{tx}")
    
    # In a real scenario, you would:
    # 1. Sign the transaction with a private key
    # 2. Submit to SuiClient for execution
    # 3. Wait for transaction confirmation
    
    print("Ready for signing and execution!")
    print()


def main():
    """Run all examples."""
    print("SuiPy Transaction Building System Examples")
    print("=" * 50)
    print()
    
    basic_transaction_example()
    complex_defi_transaction_example()
    package_management_example()
    result_chaining_example()
    serialization_round_trip_example()
    error_handling_example()
    
    # Run async example
    asyncio.run(integration_example())
    
    print("All examples completed successfully!")


if __name__ == "__main__":
    main() 