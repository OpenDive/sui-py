#!/usr/bin/env python3
"""
Example demonstrating the fixes for Result Handle assumption and object resolution.

This example shows:
1. Permissive result handle access for unknown function return counts
2. Automatic object resolution during async build
3. Offline sync building when all objects are resolved
4. Flexible API supporting both patterns
"""

import asyncio
from sui_py.transactions import TransactionBuilder
from sui_py.client import SuiClient
from sui_py.types import ObjectRef


def ref():
    return ObjectRef(
        object_id="5877400000000000000000000000000000000000000000000000000000000000",
        version=3619,
        digest="1thX6LZfHDZZGkq4tt1q2yRAPVfCTpX99XN4RHFsxM"
    )

def setup():
    tx = TransactionBuilder()
    tx.set_sender('0x2')  # Now works! Automatically padded to full address
    tx.set_gas_price(5)
    tx.set_gas_budget(100)
    tx.set_gas_payment([ref()])  # Use the ObjectRef from ref() function
    
    # Add a simple command to make it a valid transaction
    # (TypeScript SDK allows empty transactions, but this makes it more realistic)
    tx.split_coins(tx.gas_coin(), [tx.pure(1, "u64")])
    
    return tx

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
    
    # Demo 3: Sync Build Fails with Unresolved Objects
    print("3. Sync Build with Unresolved Objects:")
    print("   Trying to build synchronously with unresolved objects...")
    
    try:
        ptb = tx.build_sync()  # Should fail
        print("   ❌ Expected error but build succeeded!")
    except ValueError as e:
        print(f"   ✅ Expected error: {e}\n")
    
    # Demo 4: Async Build Would Resolve Objects
    print("4. Async Build with Object Resolution:")
    print("   Objects would be resolved automatically during async build...")
    print("   (Note: This demo shows the API without actual network calls)")
    
    # For demo purposes, we'll show what would happen with a real client
    print("   async with SuiClient('testnet') as client:")
    print("       ptb = await tx.build(client)  # Resolves objects automatically")
    print("   ✅ Clean API - automatic resolution when needed!\n")
    
    # Demo 5: Offline Building with Pre-resolved Objects
    print("5. Offline Building with Pre-resolved Objects:")
    print("   Creating transaction with pre-resolved objects...")
    
    tx2 = TransactionBuilder()
    
    # Add fully resolved object (version and digest provided)
    resolved_coin = tx2.object(
        "0x123456789abcdef",
        version=42,
        digest="AuKgNNwGR1vsRVdfo9VXJ6sokEXUF6fWPtsgQKWP74yG"  # Valid base58 digest (32 bytes when decoded)
    )
    
    # Add a simple transfer
    tx2.transfer_objects([resolved_coin], tx2.pure("0xrecipient123"))
    
    print(f"   Transaction summary:")
    print(f"   {tx2.summary()}")
    
    # This should work synchronously since all objects are resolved
    try:
        ptb2 = tx2.build_sync()  # Should work offline
        print(f"   ✅ Sync build succeeded!")
        print(f"   PTB Details:")
        print(f"     Type: {type(ptb2).__name__}")
        print(f"     Inputs: {len(ptb2.inputs)}")
        print(f"     Commands: {len(ptb2.commands)}")
        
        # Show actual input content
        if ptb2.inputs:
            print("     Input details:")
            for i, inp in enumerate(ptb2.inputs):
                print(f"       {i}: {type(inp).__name__} - {inp}")
        
        # Show actual command content  
        if ptb2.commands:
            print("     Command details:")
            for i, cmd in enumerate(ptb2.commands):
                print(f"       {i}: {type(cmd).__name__} - {cmd}")
        
        # Show serialization
        try:
            ptb_bytes = ptb2.to_bytes()
            print(f"     Serialized: {len(ptb_bytes)} bytes")
            print(f"     Hex (first 32 bytes): {ptb_bytes[:32].hex()}")
            if len(ptb_bytes) > 32:
                print(f"     Hex (last 16 bytes): ...{ptb_bytes[-16:].hex()}")
            print("   ✅ No network calls needed - built offline!")
        except Exception as e:
            print(f"     ❌ Serialization failed: {e}")
            
        # Can also use async build (though not needed)
        ptb3 = await tx2.build()  # Should also work without client
        print(f"   ✅ Async build also works: {len(ptb3.commands)} commands")
        
    except Exception as e:
        print(f"   ❌ Build failed: {e}")
    
    print("\n=== Demo Complete ===")
    print("Key improvements:")
    print("✅ Result handles are permissive (no hardcoded result_count=1)")
    print("✅ Flexible sync/async build API")
    print("✅ Automatic object resolution when client provided")
    print("✅ Offline building when all objects pre-resolved")
    print("✅ Clear error messages indicating what's needed")
    print("✅ Always produces complete, valid transactions")
    print("✅ Generates valid BCS-serialized transaction bytes")
    
    print("=== Object Ref Demo ===")
    tx = setup()
    transaction_data = await tx.build()
    bytes_data = transaction_data.to_bytes()
    print(f"   Serialized: {len(bytes_data)} bytes")
    print(f"   Hex (first 32 bytes): {bytes_data[:32].hex()}")
    if len(bytes_data) > 32:
        print(f"   Hex (last 16 bytes): ...{bytes_data[-16:].hex()}")
    print("   ✅ No network calls needed - built offline!")
# 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,88,119,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,35,14,0,0,0,0,0,0,32,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,5,0,0,0,0,0,0,0,100,0,0,0,0,0,0,0,0

if __name__ == "__main__":
    asyncio.run(main()) 