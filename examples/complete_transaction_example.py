"""
Complete Transaction Building Example

This example demonstrates how to build complete Sui transactions using
the new TransactionBuilder approach that handles all necessary metadata.

Key features shown:
- Setting transaction metadata (sender, gas budget, price, payment)
- Building complete TransactionData (not just PTB)
- Proper object references with digests
- Ready-to-sign transaction preparation
"""

import asyncio
from sui_py.transactions import TransactionBuilder
from sui_py.types import ObjectRef, SuiAddress


def simple_transfer_example():
    """
    Simple coin transfer with complete transaction metadata.
    """
    print("=== Simple Transfer Example ===")
    
    # Create transaction builder
    tx = TransactionBuilder()
    
    # Add commands
    coin = tx.object(
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        version=10,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"  # Valid base58 digest
    )
    amount = tx.pure(1000000, "u64")  # 1 SUI in MIST
    recipient = tx.pure("0x1111111111111111111111111111111111111111111111111111111111111111")
    
    # Split and transfer
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Set transaction metadata (REQUIRED for complete transactions)
    tx.set_sender("0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba")
    tx.set_gas_budget(2000000)  # 2 SUI gas budget
    tx.set_gas_price(1000)      # Standard gas price
    
    # Gas payment object
    gas_coin = ObjectRef(
        object_id="0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        version=5,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
    )
    tx.set_gas_payment([gas_coin])
    
    # Optional: Set expiration
    tx.set_expiration_epoch(1000)
    
    # Build complete transaction
    transaction_data = tx.build_sync()
    
    print(f"✅ Complete transaction built successfully!")
    print(f"   Transaction type: {type(transaction_data).__name__}")
    print(f"   Sender: {transaction_data.transaction_data_v1.sender}")
    print(f"   Gas budget: {transaction_data.transaction_data_v1.gas_data.budget}")
    print(f"   Commands: {len(transaction_data.transaction_data_v1.transaction_kind.programmable_transaction.commands)}")
    
    # Get transaction bytes ready for signing
    tx_bytes = transaction_data.to_bytes()
    print(f"   Ready for signing: {len(tx_bytes)} bytes")
    print()


def defi_interaction_example():
    """
    More complex DeFi interaction with multiple operations.
    """
    print("=== DeFi Interaction Example ===")
    
    tx = TransactionBuilder()
    
    # Input objects
    user_coin = tx.object(
        "0x1111111111111111111111111111111111111111111111111111111111111111",
        version=100,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
    )
    
    pool_object = tx.object(
        "0x2222222222222222222222222222222222222222222222222222222222222222",
        version=50,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
    )
    
    # Parameters
    liquidity_amount = tx.pure(5000000, "u64")  # 5 SUI
    min_out = tx.pure(4500000, "u64")           # Minimum 4.5 SUI out
    user_address = tx.pure("0x3333333333333333333333333333333333333333333333333333333333333333")
    
    # DeFi operations
    swap_result = tx.move_call(
        target="0x5877400000000000000000000000000000000000000000000000000000000000::swap::swap_exact_input",
        arguments=[pool_object, user_coin, liquidity_amount, min_out],
        type_arguments=["0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI", "0x5877400000000000000000000000000000000000000000000000000000000000::usdc::USDC"]
    )
    
    # Transfer result back to user
    tx.transfer_objects([swap_result[0]], user_address)
    
    # Set transaction metadata
    tx.set_sender("0x3333333333333333333333333333333333333333333333333333333333333333")
    tx.set_gas_budget(10000000)  # 10 SUI budget for complex DeFi
    tx.set_gas_price(1000)
    
    # Gas payment
    gas_payment = ObjectRef(
        object_id="0x3333333333333333333333333333333333333333333333333333333333333333",
        version=25,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
    )
    tx.set_gas_payment([gas_payment])
    
    # Build transaction
    transaction_data = tx.build_sync()
    
    print(f"✅ DeFi transaction built successfully!")
    print(f"   Sender: {transaction_data.transaction_data_v1.sender}")
    print(f"   Gas budget: {transaction_data.transaction_data_v1.gas_data.budget}")
    print(f"   Commands: {len(transaction_data.transaction_data_v1.transaction_kind.programmable_transaction.commands)}")
    print(f"   Bytes: {len(transaction_data.to_bytes())}")
    print()


async def async_transaction_example():
    """
    Example with unresolved objects that need client resolution.
    """
    print("=== Async Object Resolution Example ===")
    
    tx = TransactionBuilder()
    
    # Use objects without version/digest (unresolved)
    coin = tx.object("0x4444444444444444444444444444444444444444444444444444444444444444")
    amount = tx.pure(1000000, "u64")
    recipient = tx.pure("0x5555555555555555555555555555555555555555555555555555555555555555")
    
    # Operations with unresolved objects
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Set metadata
    tx.set_sender("0x6666666666666666666666666666666666666666666666666666666666666666")
    tx.set_gas_budget(2000000)
    tx.set_gas_price(1000)
    
    gas_coin = ObjectRef(
        object_id="0x7777777777777777777777777777777777777777777777777777777777777777",
        version=10,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
    )
    tx.set_gas_payment([gas_coin])
    
    print(f"Transaction has {len(tx._unresolved_objects)} unresolved objects")
    
    # Try to build without client (will fail)
    try:
        transaction_data = await tx.build()  # No client provided
        print("❌ Unexpected success")
    except ValueError as e:
        print(f"✅ Expected error: {str(e)[:80]}...")
    
    # In real usage, you would pass a SuiClient:
    # transaction_data = await tx.build(client)
    
    print("   Note: In production, pass a SuiClient to resolve objects automatically")
    print()


def multi_gas_payment_example():
    """
    Example with multiple gas payment objects.
    """
    print("=== Multiple Gas Payment Example ===")
    
    tx = TransactionBuilder()
    
    # Simple transfer
    coin = tx.object(
        "0x8888888888888888888888888888888888888888888888888888888888888888",
        version=1,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
    )
    amount = tx.pure(500000, "u64")
    recipient = tx.pure("0x9999999999999999999999999999999999999999999999999999999999999999")
    
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Set metadata with multiple gas coins
    tx.set_sender("0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    tx.set_gas_budget(3000000)
    tx.set_gas_price(1000)
    
    # Multiple gas payment objects
    gas_coins = [
        ObjectRef(
            object_id="0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            version=5,
            digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
        ),
        ObjectRef(
            object_id="0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
            version=8,
            digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
        )
    ]
    tx.set_gas_payment(gas_coins)
    
    # Build transaction
    transaction_data = tx.build_sync()
    
    print(f"✅ Multi-gas transaction built successfully!")
    print(f"   Gas payments: {len(transaction_data.transaction_data_v1.gas_data.payment)} objects")
    print(f"   Total size: {len(transaction_data.to_bytes())} bytes")
    print()


def sponsored_transaction_example():
    """
    Example of a sponsored transaction with different gas owner.
    """
    print("=== Sponsored Transaction Example ===")
    
    tx = TransactionBuilder()
    
    # Transaction operations (sender perspective)
    coin = tx.object(
        "0xdddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
        version=20,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
    )
    amount = tx.pure(100000, "u64")
    recipient = tx.pure("0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
    
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    # Set sender (who initiates the transaction)
    sender = "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    tx.set_sender(sender)
    
    # Set gas owner (sponsor who pays for gas)
    sponsor = "0x1010101010101010101010101010101010101010101010101010101010101010"
    tx.set_gas_owner(sponsor)
    
    # Gas configuration (paid by sponsor)
    tx.set_gas_budget(1500000)
    tx.set_gas_price(1000)
    
    sponsor_gas_coin = ObjectRef(
        object_id="0x2020202020202020202020202020202020202020202020202020202020202020",
        version=15,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
    )
    tx.set_gas_payment([sponsor_gas_coin])
    
    # Build sponsored transaction
    transaction_data = tx.build_sync()
    
    print(f"✅ Sponsored transaction built successfully!")
    print(f"   Sender: {transaction_data.transaction_data_v1.sender}")
    print(f"   Gas owner: {transaction_data.transaction_data_v1.gas_data.owner}")
    print(f"   Gas budget: {transaction_data.transaction_data_v1.gas_data.budget}")
    print(f"   Sponsored: {sender != str(transaction_data.transaction_data_v1.gas_data.owner)}")
    print()


def error_demonstration():
    """
    Show common errors and how to avoid them.
    """
    print("=== Error Handling Examples ===")
    
    # Missing sender
    try:
        tx = TransactionBuilder()
        coin = tx.object("0x1010101010101010101010101010101010101010101010101010101010101010", version=1, digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM")
        tx.transfer_objects([coin], tx.pure("0x2020202020202020202020202020202020202020202020202020202020202020"))
        # Missing: tx.set_sender()
        tx.set_gas_budget(1000000)
        tx.set_gas_price(1000)
        tx.set_gas_payment([ObjectRef("0x3030303030303030303030303030303030303030303030303030303030303030", 1, "1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM")])
        transaction_data = tx.build_sync()
    except ValueError as e:
        print(f"✅ Caught missing sender: {e}")
    
    # Missing gas budget
    try:
        tx = TransactionBuilder()
        coin = tx.object("0x4040404040404040404040404040404040404040404040404040404040404040", version=1, digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM")
        tx.transfer_objects([coin], tx.pure("0x5050505050505050505050505050505050505050505050505050505050505050"))
        tx.set_sender("0x6060606060606060606060606060606060606060606060606060606060606060")
        # Missing: tx.set_gas_budget()
        tx.set_gas_price(1000)
        tx.set_gas_payment([ObjectRef("0x7070707070707070707070707070707070707070707070707070707070707070", 1, "1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM")])
        transaction_data = tx.build_sync()
    except ValueError as e:
        print(f"✅ Caught missing gas budget: {e}")
    
    # Empty transaction
    try:
        tx = TransactionBuilder()
        # No commands added
        tx.set_sender("0x8080808080808080808080808080808080808080808080808080808080808080")
        tx.set_gas_budget(1000000)
        tx.set_gas_price(1000)
        tx.set_gas_payment([ObjectRef("0x9090909090909090909090909090909090909090909090909090909090909090", 1, "1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM")])
        transaction_data = tx.build_sync()
    except ValueError as e:
        print(f"✅ Caught empty transaction: {e}")
    
    print("   All expected errors caught correctly!")
    print()


async def main():
    """Run all complete transaction examples."""
    print("Complete Transaction Building Examples")
    print("=" * 45)
    print()
    
    simple_transfer_example()
    defi_interaction_example()
    await async_transaction_example()
    multi_gas_payment_example()
    sponsored_transaction_example()
    error_demonstration()
    
    print("🎉 All examples completed successfully!")
    print()
    print("Next steps:")
    print("1. Sign the transaction bytes with a private key")
    print("2. Submit the signed transaction to Sui network")
    print("3. Wait for transaction confirmation")


if __name__ == "__main__":
    asyncio.run(main()) 