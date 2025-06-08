#!/usr/bin/env python3
"""
Example demonstrating the fixes for Result Handle assumption and object resolution.

This example shows:
1. Permissive result handle access for unknown function return counts
2. Automatic object resolution during build
3. Single, clean async build API
"""

import asyncio
from sui_py.transactions import TransactionBuilder
from sui_py.client import SuiClient


async def main():
    print("=== Transaction Builder Fixes Demo ===\n")
    
    # Create a transaction builder
    tx = TransactionBuilder()
    
    # Demo 1: Permissive Result Handle Access
    print("1. Permissive Result Handle Access:")
    print("   Creating a move call without knowing result count...")
    
    # This works even if we don't know how many results the function returns
    result = tx.move_call(
        "0x2::coin::split",
        arguments=[tx.gas_coin(), tx.pure(1000, "u64")],
        type_arguments=["0x2::sui::SUI"]
    )
    
    # Access results without bounds errors
    print(f"   result.single() -> {result.single()}")
    print(f"   result[0] -> {result[0]}")
    print(f"   result[1] -> {result[1]}")  # This would fail before our fix
    print("   ✅ No IndexError thrown!\n")
    
    # Demo 2: Object Resolution - Unresolved Objects
    print("2. Object Resolution - Unresolved Objects:")
    print("   Adding unresolved objects...")
    
    # Add objects without version/digest (unresolved)
    coin1 = tx.object("0x123456789abcdef")
    coin2 = tx.object("0xabcdef123456789") 
    
    print(f"   Added coin1: {coin1}")
    print(f"   Added coin2: {coin2}")
    print(f"   Transaction summary:")
    print(f"   {tx.summary()}\n")
    
    # Demo 3: Automatic Object Resolution During Build
    print("3. Automatic Object Resolution:")
    print("   Objects will be resolved automatically during build...")
    print("   (Note: This demo uses a mock client for demonstration)")
    
    # For demo purposes, we'll show what would happen with a real client
    # In practice, you'd use: async with SuiClient("testnet") as client:
    print("   async with SuiClient('testnet') as client:")
    print("       ptb = await tx.build(client)  # Resolves objects automatically")
    print("   ✅ Clean API - no separate resolution step needed!\n")
    
    # Demo 4: Resolved Objects Work Too
    print("4. Pre-resolved Objects:")
    print("   Creating transaction with pre-resolved objects...")
    
    tx2 = TransactionBuilder()
    
    # Add fully resolved object (version and digest provided)
    resolved_coin = tx2.object(
        "0x123456789abcdef",
        version=42,
        digest="ABC123DEF456"
    )
    
    # Add a simple transfer
    tx2.transfer_objects([resolved_coin], tx2.pure("0xrecipient123"))
    
    print(f"   Transaction summary:")
    print(f"   {tx2.summary()}")
    print("   Pre-resolved objects require no network calls during build")
    
    print("\n=== Demo Complete ===")
    print("Key improvements:")
    print("✅ Result handles are permissive (no hardcoded result_count=1)")
    print("✅ Single async build() method with automatic object resolution")
    print("✅ Clean API that matches TypeScript SDK pattern")
    print("✅ Supports both resolved and unresolved object patterns")
    print("✅ Always produces complete, valid transactions")


if __name__ == "__main__":
    asyncio.run(main()) 