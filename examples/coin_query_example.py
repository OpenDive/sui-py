"""
Comprehensive example of the SuiPy Coin Query API.

This script demonstrates how to use the async Coin Query client for:

BASIC OPERATIONS:
- Get all balances for an address
- Get specific coin balances  
- Query coin metadata
- Get total supply information

ADVANCED FEATURES:
- Type-safe operations with explicit typing
- Pagination through large result sets
- Balance formatting using metadata
- Comprehensive error handling
- Type safety demonstrations
"""

import asyncio
from typing import List

from sui_py import (
    SuiClient, SuiError, SuiValidationError, SuiRPCError,
    SuiAddress, Balance, Coin, SuiCoinMetadata, Supply, Page
)


async def basic_coin_operations():
    """Demonstrate basic coin query operations."""
    
    print("🔹 BASIC COIN OPERATIONS")
    print("=" * 50)
    
    # Example Sui address (replace with a real address for testing)
    example_address = "0x94f1a597b4e8f709a396f7f6b1482bdcd65a673d111e49286c527fab7c2d0961"
    
    # Initialize client for mainnet
    async with SuiClient("mainnet") as client:
        print(f"Connected to: {client.endpoint}")
        print()
        
        try:
            # Get all balances for the address
            print("=== Getting all balances ===")
            balances: List[Balance] = await client.coin_query.get_all_balances(example_address)
            
            if balances:
                print(f"Found {len(balances)} coin types:")
                for balance in balances:
                    print(f"  • {balance.coin_type}")
                    print(f"    Objects: {balance.coin_object_count}")
                    print(f"    Balance: {balance.total_balance}")
                    print(f"    Is zero: {balance.is_zero()}")
                    print()
            else:
                print("No balances found for this address.")
                print()
            
            # Get SUI balance specifically
            print("=== Getting SUI balance ===")
            sui_balance: Balance = await client.coin_query.get_balance(example_address)
            print(f"SUI Balance: {sui_balance.total_balance}")
            print(f"SUI Coin Count: {sui_balance.coin_object_count}")
            print(f"Is zero balance: {sui_balance.is_zero()}")
            print()
            
            # Get SUI coin metadata
            print("=== Getting SUI metadata ===")
            sui_type = "0x2::sui::SUI"
            sui_metadata: SuiCoinMetadata = await client.coin_query.get_coin_metadata(sui_type)
            print(f"Name: {sui_metadata.name}")
            print(f"Symbol: {sui_metadata.symbol}")
            print(f"Decimals: {sui_metadata.decimals}")
            print(f"Description: {sui_metadata.description}")
            if sui_metadata.icon_url:
                print(f"Icon: {sui_metadata.icon_url}")
            print()
            
            # Format balance using metadata
            if not sui_balance.is_zero():
                formatted_balance = sui_metadata.format_amount(sui_balance.total_balance_int)
                print(f"Formatted SUI balance: {formatted_balance:.{sui_metadata.decimals}f} {sui_metadata.symbol}")
                print()
            
            # Get total supply of SUI
            print("=== Getting SUI total supply ===")
            supply: Supply = await client.coin_query.get_total_supply(sui_type)
            print(f"Total SUI Supply: {supply.value}")
            
            # Format supply using metadata
            formatted_supply = supply.format_with_metadata(sui_metadata)
            print(f"Formatted supply: {formatted_supply:.2f} {sui_metadata.symbol}")
            print()
            
        except SuiRPCError as e:
            print(f"RPC error occurred: {e}")
        except SuiError as e:
            print(f"Sui error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def advanced_coin_operations():
    """Demonstrate advanced coin query features."""
    
    print("🔸 ADVANCED COIN OPERATIONS")
    print("=" * 50)
    
    # Use a well-known address for demonstration
    example_address = "0x94f1a597b4e8f709a396f7f6b1482bdcd65a673d111e49286c527fab7c2d0961"
    
    async with SuiClient("mainnet") as client:
        try:
            # Demonstrate pagination with coins
            print("=== Paginated coin queries ===")
            coins_page: Page[Coin] = await client.coin_query.get_all_coins(
                owner=example_address,
                limit=3
            )
            
            print(f"Page has {len(coins_page.data)} coins")
            print(f"Has next page: {coins_page.has_next_page}")
            if coins_page.next_cursor:
                print(f"Next cursor: {coins_page.next_cursor}")
            
            for i, coin in enumerate(coins_page.data):
                print(f"  Coin {i+1}:")
                print(f"    ID: {coin.coin_object_id}")
                print(f"    Balance: {coin.balance}")
                print(f"    Type: {coin.coin_type}")
                print(f"    Version: {coin.version}")
                print(f"    Previous TX: {coin.previous_transaction}")
                print()
            
            # Demonstrate multi-page pagination
            print("=== Multi-page pagination demo ===")
            page_count = 1
            current_page = coins_page
            
            while current_page.has_next_page and page_count <= 3:  # Limit demo to 3 pages
                print(f"Getting page {page_count + 1}...")
                
                current_page = await client.coin_query.get_all_coins(
                    owner=example_address,
                    cursor=current_page.next_cursor,
                    limit=3
                )
                
                print(f"Page {page_count + 1}: {len(current_page.data)} coins")
                for coin in current_page.data:
                    print(f"  - {coin.coin_type}: {coin.balance}")
                
                page_count += 1
            
            if page_count > 3:
                print("  ... (limiting demo to 3 pages)")
            
            print(f"Total pages processed: {page_count}")
            print()
            
            # Demonstrate specific coin type queries
            print("=== Specific coin type queries ===")
            sui_coins: Page[Coin] = await client.coin_query.get_coins(
                owner=example_address,
                coin_type="0x2::sui::SUI",
                limit=5
            )
            
            print(f"Found {len(sui_coins.data)} SUI coins:")
            for coin in sui_coins.data:
                print(f"  - ID: {coin.coin_object_id}")
                print(f"    Balance: {coin.balance}")
                print()
                
        except SuiRPCError as e:
            print(f"RPC error: {e}")
        except SuiError as e:
            print(f"Sui error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def demonstrate_type_safety():
    """Demonstrate type safety features and error handling."""
    
    print("🔷 TYPE SAFETY DEMONSTRATION")
    print("=" * 50)
    
    # Demonstrate address validation
    print("=== Address validation ===")
    
    try:
        # This will raise a validation error
        invalid_address = SuiAddress.from_str("invalid_address")
        print(f"❌ Unexpected success: {invalid_address}")
    except SuiValidationError as e:
        print(f"✅ Caught invalid address: {e}")
    
    try:
        # This should work (address gets padded)
        short_address = SuiAddress.from_str("0x123")
        print(f"✅ Short address accepted (padded): {short_address}")
    except SuiValidationError as e:
        print(f"❌ Unexpected validation error: {e}")
    
    # Valid address creation
    valid_address = SuiAddress.from_str(
        "0x94f1a597b4e8f709a396f7f6b1482bdcd65a673d111e49286c527fab7c2d0961"
    )
    print(f"✅ Valid address: {valid_address}")
    print()
    
    # Demonstrate Balance object methods
    print("=== Balance object demonstration ===")
    balance_data = {
        "coinType": "0x2::sui::SUI",
        "coinObjectCount": 5,
        "totalBalance": "1000000000",  # 1 SUI in MIST
        "lockedBalance": {}
    }
    
    balance = Balance.from_dict(balance_data)
    print(f"✅ Balance created: {balance.total_balance}")
    print(f"✅ Balance as int: {balance.total_balance_int}")
    print(f"✅ Is zero: {balance.is_zero()}")
    print(f"✅ Coin count: {balance.coin_object_count}")
    print()
    
    # Demonstrate metadata formatting
    print("=== Metadata formatting demonstration ===")
    metadata_data = {
        "decimals": 9,
        "name": "Sui",
        "symbol": "SUI", 
        "description": "The native token of Sui",
        "id": "0x94f1a597b4e8f709a396f7f6b1482bdcd65a673d111e49286c527fab7c2d0961"
    }
    
    metadata = SuiCoinMetadata.from_dict(metadata_data)
    formatted_amount = metadata.format_amount(balance.total_balance_int)
    print(f"✅ Formatted amount: {formatted_amount} {metadata.symbol}")
    
    # Demonstrate parsing back
    parsed_amount = metadata.parse_amount(formatted_amount)
    print(f"✅ Parsed back to base units: {parsed_amount}")
    print()


async def main():
    """Main example function that runs all demonstrations."""
    
    print("SuiPy Comprehensive Coin Query API Example")
    print("=" * 60)
    print()
    
    # Run basic operations
    await basic_coin_operations()
    print("\n" + "=" * 60 + "\n")
    
    # Run advanced operations  
    await advanced_coin_operations()
    print("\n" + "=" * 60 + "\n")
    
    # Run type safety demonstration
    await demonstrate_type_safety()


if __name__ == "__main__":
    asyncio.run(main()) 