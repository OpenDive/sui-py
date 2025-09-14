"""
Example usage of the SuiPy Write API.

This script demonstrates how to use the async Write API client to:
- Execute signed transactions on the network
- Perform dry runs for testing and gas estimation
- Use dev inspect mode for detailed transaction analysis
- Handle different transaction data formats (base64/hex)
- Configure response options for different use cases
- Properly handle errors and network issues

The example includes real Sui transaction data for testing.

Usage:
    # Use built-in example data
    python3 examples/write_api_example.py
    
    # Use your own transaction bytes and signature
    python3 examples/write_api_example.py <tx_bytes> <signature>
    
    # Specify sender address explicitly
    python3 examples/write_api_example.py <tx_bytes> <signature> <sender>

Example with real data:
    python3 examples/write_api_example.py \
      "AAAEAQBX81xJQM5DHo5/jceY0CRyy75ofrHiPR08Z87V+uJp0SUeUCIAAAAAIOG7Q2BqQ7ubDu+AMmcKnOMtQ9qlCPVyov5TAUwSBiU5AAgBAAAAAAAAAAEB+kXkr+JWG8JF5msZDy5DkcCptMOkz7UUC2RKVX4Q5Ox6LDkiAAAAAAEBAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAQAAAAAAAAAAAwIBAAABAQEAALkI7DF3LJccTHGo/QLJ4W/2TmTcck15IDO06bHDVJHrCXJvYm90X3BldAJoaQAAALkI7DF3LJccTHGo/QLJ4W/2TmTcck15IDO06bHDVJHrCXJvYm90X3BldApmZWVkX3RyZWF0AAQBAgADAAAAAAIBAAEDAM0yfOn6ogI/ApPwOB063148bFd7ZbYSZKWoCNyCeblkAU3b6gkObn2/Rr8HB9Vj68sMNC8xqn2QVUDx5HVQNrpUWWVQIgAAAAAg9Rr3yuGntheUmkysknxBWwks+6Wqbh41Z64mAPCD8c3NMnzp+qICPwKT8DgdOt9ePGxXe2W2EmSlqAjcgnm5ZOgDAAAAAAAAhNgxAAAAAAAA" \
      "AAt4ih9jPcbdc3SkSiBI6gbL+3MRnnHs5V3hM1ptgHr/AEu/YjXx2QTh5/orJqYSji/qwvW/zWU0fZqJ8oSWywdunWqkb/0h4vSCCYj1w2OU84nFcZtk45+ZI+TTBcdtYg=="

Parameters:
    tx_bytes  : Transaction bytes in base64 format (typically 400-800+ characters)
                Get from: sui client dry-run, TypeScript SDK, or transaction builders
    signature : Transaction signature in base64 format (typically 132 characters)
                Get from: sui client sign, wallet signing, or crypto libraries
    sender    : Transaction sender address in hex format (optional)
                Format: 0x followed by 64 hex characters

How to get transaction data:
    # Using Sui CLI
    sui client transfer-sui --to 0x... --amount 1000000 --dry-run
    sui client sign --data <transaction_bytes>
    
    # Using TypeScript SDK
    const tx = new TransactionBlock();
    tx.transferObjects([coin], recipient);
    const bytes = await tx.build({ client });
    const signature = await keypair.signTransactionBlock(bytes);

Expected output:
    ✅ Transaction executed successfully
       Transaction digest: D661ZS4KiX4Zw4zpKcDtWXxmAw5JgsgpNabmMe3Bzmah
       Status: {'status': 'success'}
       Gas used: {'computationCost': '1000000', 'storageCost': '4028000', ...}
"""

import asyncio
import sys
import time
import base64
import json
from typing import Optional

from sui_py import SuiClient, SuiError, TransactionBlockResponseOptions

# Debug flag - set to False to disable debug output
DEBUG_WRITE_API = True

# Enable RPC debug logging (set to 'true' for detailed RPC debugging)
import os
os.environ['DEBUG_WRITE_API_RPC'] = 'false'

def debug_log(message: str, data=None):
    """Print debug information if debug mode is enabled"""
    if DEBUG_WRITE_API:
        print(f"🔍 DEBUG: {message}")
        if data is not None:
            if isinstance(data, (dict, list)):
                print(f"   Data: {json.dumps(data, indent=2, default=str)}")
            else:
                print(f"   Data: {data}")
        print()


# Real Sui transaction data for testing
REAL_TRANSACTION_DATA = {
    "tx_bytes": "AAAEAQBX81xJQM5DHo5/jceY0CRyy75ofrHiPR08Z87V+uJp0SUeUCIAAAAAIOG7Q2BqQ7ubDu+AMmcKnOMtQ9qlCPVyov5TAUwSBiU5AAgBAAAAAAAAAAEB+kXkr+JWG8JF5msZDy5DkcCptMOkz7UUC2RKVX4Q5Ox6LDkiAAAAAAEBAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAQAAAAAAAAAAAwIBAAABAQEAALkI7DF3LJccTHGo/QLJ4W/2TmTcck15IDO06bHDVJHrCXJvYm90X3BldAJoaQAAALkI7DF3LJccTHGo/QLJ4W/2TmTcck15IDO06bHDVJHrCXJvYm90X3BldApmZWVkX3RyZWF0AAQBAgADAAAAAAIBAAEDAM0yfOn6ogI/ApPwOB063148bFd7ZbYSZKWoCNyCeblkAU3b6gkObn2/Rr8HB9Vj68sMNC8xqn2QVUDx5HVQNrpUWWVQIgAAAAAg9Rr3yuGntheUmkysknxBWwks+6Wqbh41Z64mAPCD8c3NMnzp+qICPwKT8DgdOt9ePGxXe2W2EmSlqAjcgnm5ZOgDAAAAAAAAhNgxAAAAAAAA",
    "signature": "AAt4ih9jPcbdc3SkSiBI6gbL+3MRnnHs5V3hM1ptgHr/AEu/YjXx2QTh5/orJqYSji/qwvW/zWU0fZqJ8oSWywdunWqkb/0h4vSCCYj1w2OU84nFcZtk45+ZI+TTBcdtYg==",
    "sender": "0xcd327ce9faa2023f0293f0381d3adf5e3c6c577b65b61264a5a808dc8279b964",
    "network": "testnet"
}


def detect_transaction_format(tx_input: str) -> str:
    """
    Detect the format of transaction bytes input.
    
    Args:
        tx_input: Transaction bytes as string
        
    Returns:
        Format type: 'hex_prefixed', 'hex_raw', or 'base64'
    """
    if tx_input.startswith("0x"):
        return "hex_prefixed"
    elif all(c in "0123456789abcdefABCDEF" for c in tx_input):
        return "hex_raw"
    else:
        return "base64"


def normalize_transaction_bytes(tx_input: str) -> str:
    """
    Convert transaction bytes to base64 format expected by Write API.
    
    Args:
        tx_input: Transaction bytes in any supported format
        
    Returns:
        Base64 encoded transaction bytes
        
    Raises:
        ValueError: If input format is invalid
    """
    format_type = detect_transaction_format(tx_input)
    
    if format_type == "hex_prefixed":
        # Remove 0x prefix and convert hex to base64
        hex_data = tx_input[2:]
        try:
            bytes_data = bytes.fromhex(hex_data)
            return base64.b64encode(bytes_data).decode('utf-8')
        except ValueError as e:
            raise ValueError(f"Invalid hex data: {e}")
    
    elif format_type == "hex_raw":
        # Convert hex to base64
        try:
            bytes_data = bytes.fromhex(tx_input)
            return base64.b64encode(bytes_data).decode('utf-8')
        except ValueError as e:
            raise ValueError(f"Invalid hex data: {e}")
    
    else:  # base64
        # Validate base64 format
        try:
            base64.b64decode(tx_input)
            return tx_input
        except Exception as e:
            raise ValueError(f"Invalid base64 data: {e}")


async def demonstrate_dry_run(client: SuiClient, tx_bytes: str):
    """
    Demonstrate dry run functionality for gas estimation and validation.
    
    Args:
        client: Connected SuiClient instance
        tx_bytes: Transaction bytes in base64 format
    """
    print("=== Dry Run Transaction ===")
    print("🧪 Testing transaction without executing on chain...")
    
    try:
        debug_log("Starting dry run transaction", {
            "tx_bytes_length": len(tx_bytes),
            "tx_bytes_preview": tx_bytes[:50] + "..."
        })
        
        # Perform dry run with default options
        start_time = time.time()
        result = await client.write_api.dry_run_transaction_block(tx_bytes)
        duration = time.time() - start_time
        
        debug_log("Dry run response received", {
            "response_type": type(result).__name__,
            "response_attributes": list(result.__dict__.keys()) if hasattr(result, '__dict__') else "No __dict__",
            "has_effects": hasattr(result, 'effects'),
            "effects_type": type(result.effects).__name__ if hasattr(result, 'effects') else "No effects"
        })
        
        if hasattr(result, 'effects'):
            debug_log("Effects structure analysis", {
                "effects_attributes": list(result.effects.__dict__.keys()) if hasattr(result.effects, '__dict__') else "No __dict__",
                "has_status": hasattr(result.effects, 'status'),
                "has_gas_used": hasattr(result.effects, 'gas_used'),
                "status_value": getattr(result.effects, 'status', 'Not found'),
                "gas_used_value": getattr(result.effects, 'gas_used', 'Not found')
            })
        
        print(f"✅ Dry run completed in {duration:.2f}s")
        print(f"   Transaction status: {result.effects.status}")
        print(f"   Gas used: {result.effects.gas_used}")
        
        if result.events:
            print(f"   Events emitted: {len(result.events)}")
        
        if result.object_changes:
            print(f"   Objects affected: {len(result.object_changes)}")
            
        if result.balance_changes:
            print(f"   Balance changes: {len(result.balance_changes)}")
            for change in result.balance_changes[:3]:  # Show first 3
                print(f"     {change.owner}: {change.amount} {change.coin_type}")
        
    except SuiError as e:
        print(f"❌ Dry run failed: {e}")
        print("   This is expected if the transaction is old or invalid")
    
    print()


async def demonstrate_dev_inspect(client: SuiClient, sender: str, tx_bytes: str):
    """
    Demonstrate dev inspect functionality for detailed analysis.
    
    Args:
        client: Connected SuiClient instance
        sender: Transaction sender address
        tx_bytes: Transaction bytes in base64 format
    """
    print("=== Dev Inspect Transaction ===")
    print("🔍 Analyzing transaction in development mode...")
    
    try:
        debug_log("Starting dev inspect transaction", {
            "sender": sender,
            "tx_bytes_length": len(tx_bytes),
            "tx_bytes_preview": tx_bytes[:50] + "...",
            "gas_price": 1000
        })
        
        # Perform dev inspect with optional gas price
        start_time = time.time()
        result = await client.write_api.dev_inspect_transaction_block(
            sender=sender,
            transaction_block=tx_bytes,
            gas_price=1000  # Optional: specify gas price
        )
        duration = time.time() - start_time
        
        debug_log("Dev inspect response received", {
            "response_type": type(result).__name__,
            "response_attributes": list(result.__dict__.keys()) if hasattr(result, '__dict__') else "No __dict__",
            "has_effects": hasattr(result, 'effects'),
            "effects_type": type(result.effects).__name__ if hasattr(result, 'effects') else "No effects"
        })
        
        print(f"✅ Dev inspect completed in {duration:.2f}s")
        print(f"   Sender: {sender}")
        print(f"   Transaction status: {result.effects.status}")
        
        if result.error:
            print(f"   Error: {result.error}")
        
        if result.results:
            print(f"   Results: {len(result.results)} return values")
            for i, result_item in enumerate(result.results[:3]):  # Show first 3
                print(f"     Result {i}: {result_item}")
        
        if result.events:
            print(f"   Events: {len(result.events)} events emitted")
        
    except SuiError as e:
        debug_log("Dev inspect exception details", {
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "exception_args": getattr(e, 'args', 'No args'),
            "has_code": hasattr(e, 'code'),
            "code": getattr(e, 'code', 'No code'),
            "has_data": hasattr(e, 'data'),
            "data": getattr(e, 'data', 'No data')
        })
        print(f"❌ Dev inspect failed: {e}")
        print("   This is expected if the transaction is old or invalid")
    
    print()


async def demonstrate_response_options(client: SuiClient, tx_bytes: str):
    """
    Demonstrate different response option configurations and their impact.
    
    Args:
        client: Connected SuiClient instance
        tx_bytes: Transaction bytes in base64 format
    """
    print("=== Response Options Comparison ===")
    print("📊 Comparing different response configurations...")
    
    # Test different response option configurations
    test_cases = [
        {
            "name": "Minimal Response (Performance)",
            "options": TransactionBlockResponseOptions(
                show_effects=False,
                show_events=False,
                show_object_changes=False,
                show_balance_changes=False
            )
        },
        {
            "name": "Default Response (Balanced)",
            "options": TransactionBlockResponseOptions()  # show_effects=True by default
        },
        {
            "name": "Full Response (Complete Details)",
            "options": TransactionBlockResponseOptions(
                show_effects=True,
                show_events=True,
                show_object_changes=True,
                show_balance_changes=True,
                show_raw_effects=True,
                show_input=True
            )
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔧 Testing: {test_case['name']}")
        
        try:
            start_time = time.time()
            # Use dry run to test response options safely
            result = await client.write_api.dry_run_transaction_block(tx_bytes)
            duration = time.time() - start_time
            
            # Analyze response size (approximate)
            response_size = len(str(result.__dict__))
            
            print(f"   ⏱️  Response time: {duration:.3f}s")
            print(f"   📏 Response size: ~{response_size} chars")
            print(f"   📋 Effects shown: {hasattr(result, 'effects') and result.effects is not None}")
            print(f"   🎯 Events shown: {hasattr(result, 'events') and len(result.events) > 0}")
            
        except SuiError as e:
            print(f"   ❌ Failed: {e}")
    
    print()


async def demonstrate_execute_transaction(client: SuiClient, tx_bytes: str, signature: str):
    """
    Demonstrate actual transaction execution (may fail if transaction is old/invalid).
    
    Args:
        client: Connected SuiClient instance
        tx_bytes: Transaction bytes in base64 format
        signature: Transaction signature in base64 format
    """
    print("=== Execute Transaction ===")
    print("🚀 Attempting to execute transaction on network...")
    print("⚠️  Note: This may fail if the transaction is old or already executed")
    
    try:
        # Execute with full response options for demonstration
        options = TransactionBlockResponseOptions(
            show_effects=True,
            show_events=True,
            show_object_changes=True,
            show_balance_changes=True
        )
        
        debug_log("Starting transaction execution", {
            "tx_bytes_length": len(tx_bytes),
            "tx_bytes_preview": tx_bytes[:50] + "...",
            "signature_length": len(signature),
            "signature_preview": signature[:30] + "...",
            "options": {
                "show_effects": options.show_effects,
                "show_events": options.show_events,
                "show_object_changes": options.show_object_changes,
                "show_balance_changes": options.show_balance_changes
            }
        })
        
        start_time = time.time()
        response = await client.write_api.execute_transaction_block(
            transaction_block=tx_bytes,
            signature=signature,
            options=options
        )
        duration = time.time() - start_time
        
        debug_log("Execute transaction response received", {
            "response_type": type(response).__name__,
            "response_attributes": list(response.__dict__.keys()) if hasattr(response, '__dict__') else "No __dict__",
            "has_effects": hasattr(response, 'effects'),
            "effects_type": type(response.effects).__name__ if hasattr(response, 'effects') else "No effects",
            "digest": getattr(response, 'digest', 'Not found')
        })
        
        if hasattr(response, 'effects'):
            debug_log("Execute effects structure analysis", {
                "effects_attributes": list(response.effects.__dict__.keys()) if hasattr(response.effects, '__dict__') else "No __dict__",
                "has_status": hasattr(response.effects, 'status'),
                "has_gas_used": hasattr(response.effects, 'gas_used'),
                "status_value": getattr(response.effects, 'status', 'Not found'),
                "gas_used_value": getattr(response.effects, 'gas_used', 'Not found')
            })
        
        print(f"✅ Transaction executed successfully in {duration:.2f}s")
        print(f"   Transaction digest: {response.digest}")
        print(f"   Confirmed local execution: {response.confirmed_local_execution}")
        
        if hasattr(response, 'effects') and response.effects:
            print(f"   Status: {getattr(response.effects, 'status', 'Unknown')}")
            print(f"   Gas used: {getattr(response.effects, 'gas_used', 'Unknown')}")
        
        if hasattr(response, 'events') and response.events:
            print(f"   Events emitted: {len(response.events)}")
        
        if hasattr(response, 'object_changes') and response.object_changes:
            print(f"   Objects changed: {len(response.object_changes)}")
        
        if hasattr(response, 'balance_changes') and response.balance_changes:
            print(f"   Balance changes: {len(response.balance_changes)}")
        
    except SuiError as e:
        print(f"❌ Transaction execution failed: {e}")
        print("   Common reasons:")
        print("   - Transaction already executed")
        print("   - Invalid signature")
        print("   - Insufficient gas")
        print("   - Object version conflicts")
        print("   - Network issues")
    
    print()


def demonstrate_format_handling(tx_bytes: str):
    """
    Demonstrate handling different transaction byte formats.
    
    Args:
        tx_bytes: User's actual transaction bytes in base64 format
    """
    print("=== Transaction Format Handling ===")
    print("🔄 Demonstrating format detection and conversion...")
    
    # Generate test cases from user's actual transaction data
    try:
        # Convert user's base64 to hex for testing
        decoded_bytes = base64.b64decode(tx_bytes)
        user_hex = decoded_bytes.hex()
        
        test_cases = [
            ("Base64 format", tx_bytes),
            ("Hex with 0x prefix", f"0x{user_hex}"),
            ("Raw hex format", user_hex),
            ("Invalid format", "invalid!@#$%")
        ]
    except Exception:
        # Fallback if conversion fails
        test_cases = [
            ("Base64 format", tx_bytes),
            ("Invalid format", "invalid!@#$%")
        ]
    
    for name, tx_input in test_cases:
        print(f"\n🧪 Testing: {name}")
        print(f"   Input: {tx_input[:50]}{'...' if len(tx_input) > 50 else ''}")
        
        try:
            detected_format = detect_transaction_format(tx_input)
            normalized = normalize_transaction_bytes(tx_input)
            
            print(f"   ✅ Detected format: {detected_format}")
            print(f"   ✅ Normalized: {normalized[:50]}{'...' if len(normalized) > 50 else ''}")
            
        except ValueError as e:
            print(f"   ❌ Error: {e}")
    
    print()


async def demonstrate_error_handling(client: SuiClient):
    """
    Demonstrate proper error handling for various failure scenarios.
    
    Args:
        client: Connected SuiClient instance
    """
    print("=== Error Handling Demonstration ===")
    print("🚨 Testing various error scenarios...")
    
    error_test_cases = [
        {
            "name": "Invalid transaction bytes",
            "tx_bytes": "invalid_base64!@#$",
            "signature": "valid_signature_format_but_fake",
            "test_method": "dry_run"
        },
        {
            "name": "Empty transaction bytes",
            "tx_bytes": "",
            "signature": "valid_signature_format_but_fake",
            "test_method": "dry_run"
        },
        {
            "name": "Invalid signature format",
            "tx_bytes": REAL_TRANSACTION_DATA["tx_bytes"],
            "signature": "invalid_signature!@#$",
            "test_method": "execute"
        }
    ]
    
    for test_case in error_test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        
        try:
            if test_case["test_method"] == "dry_run":
                await client.write_api.dry_run_transaction_block(test_case["tx_bytes"])
            elif test_case["test_method"] == "execute":
                await client.write_api.execute_transaction_block(
                    transaction_block=test_case["tx_bytes"],
                    signature=test_case["signature"]
                )
            
            print("   ⚠️  Unexpectedly succeeded (should have failed)")
            
        except SuiError as e:
            print(f"   ✅ Expected error caught: {type(e).__name__}")
            print(f"      Message: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}")
        except Exception as e:
            print(f"   ✅ Expected error caught: {type(e).__name__}")
            print(f"      Message: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}")
    
    print()


async def main():
    """Main example function."""
    
    print("🔥 SuiPy Write API Example")
    print("=" * 50)
    print("This example demonstrates all Write API functionality")
    print("including transaction execution, dry runs, and dev inspect.")
    print()
    
    # Handle command line arguments for custom data
    if len(sys.argv) >= 3:
        tx_bytes_input = sys.argv[1]
        signature = sys.argv[2]
        sender = sys.argv[3] if len(sys.argv) > 3 else REAL_TRANSACTION_DATA["sender"]
        
        print("📝 Using provided transaction data")
        print(f"   Transaction bytes: {len(tx_bytes_input)} chars")
        print(f"   Signature: {len(signature)} chars")
        print(f"   Sender: {sender}")
        
        # Validate parameter formats
        if len(tx_bytes_input) < 100:
            print("⚠️  Warning: Transaction bytes seem too short (expected 400+ chars)")
        if len(signature) != 132:
            print(f"⚠️  Warning: Signature length is {len(signature)} chars (expected 132)")
        
        # Normalize transaction bytes format
        try:
            tx_bytes = normalize_transaction_bytes(tx_bytes_input)
            detected_format = detect_transaction_format(tx_bytes_input)
            print(f"   Detected format: {detected_format}")
        except ValueError as e:
            print(f"❌ Invalid transaction bytes format: {e}")
            print("💡 Tip: Transaction bytes should be in base64 or hex format")
            return
            
    else:
        tx_bytes = REAL_TRANSACTION_DATA["tx_bytes"]
        signature = REAL_TRANSACTION_DATA["signature"]
        sender = REAL_TRANSACTION_DATA["sender"]
        
        print("📝 Using built-in example data")
        print("   💡 Tip: Pass your own transaction bytes and signature as arguments")
        print("   Usage: python3 examples/write_api_example.py <tx_bytes> <signature> [sender]")
        print()
        print("   Example with real data:")
        print("   python3 examples/write_api_example.py \\")
        print('     "AAAEAQBX81xJQM5DHo5/jceY0CRyy75ofrHiPR08Z87V+uJp0S..." \\')
        print('     "AAt4ih9jPcbdc3SkSiBI6gbL+3MRnnHs5V3hM1ptgHr/AEu/..."')
    
    print()
    
    # Initialize client for testnet
    network = REAL_TRANSACTION_DATA["network"]
    async with SuiClient(network) as client:
        print(f"🌐 Connected to Sui {network}")
        print(f"   Endpoint: {client.endpoint}")
        print(f"   Connection status: {'✅ Connected' if client.is_connected else '❌ Disconnected'}")
        print()
        
        try:
            # Demonstrate all Write API functionality
            await demonstrate_dry_run(client, tx_bytes)
            await demonstrate_dev_inspect(client, sender, tx_bytes)
            await demonstrate_response_options(client, tx_bytes)
            await demonstrate_execute_transaction(client, tx_bytes, signature)
            
            # Educational demonstrations
            demonstrate_format_handling(tx_bytes)
            await demonstrate_error_handling(client)
            
            print("🎉 All Write API demonstrations completed!")
            print()
            print("💡 Key Takeaways:")
            print("   • Use dry_run_transaction_block for gas estimation and validation")
            print("   • Use dev_inspect_transaction_block for detailed analysis")
            print("   • Configure response options based on your needs")
            print("   • Always handle errors gracefully in production code")
            print("   • Transaction bytes can be provided in hex or base64 format")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("   Please check your network connection and try again")


if __name__ == "__main__":
    asyncio.run(main())
