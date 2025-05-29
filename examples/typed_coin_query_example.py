"""
Example demonstrating the typed Coin Query API.

This example shows how to use the SuiPy SDK with typed schemas for better
type safety and developer experience.
"""

import asyncio
from typing import List

from sui_py import (
    SuiClient, 
    SuiAddress, 
    Balance, 
    Coin, 
    SuiCoinMetadata, 
    Supply, 
    Page,
    SuiValidationError,
    SuiRPCError
)
from sui_py.constants import NETWORK_ENDPOINTS


async def demonstrate_typed_coin_queries():
    """Demonstrate various typed coin query operations."""
    
    # Initialize client
    async with SuiClient(NETWORK_ENDPOINTS["mainnet"]) as client:
        
        # Example address (replace with a real address for testing)
        address = SuiAddress.from_str("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        
        try:
            print("=== Typed Coin Query API Demo ===\n")
            
            # 1. Get all balances with type safety
            print("1. Getting all balances...")
            balances: List[Balance] = await client.coin_query.get_all_balances(address)
            
            print(f"Found {len(balances)} coin types:")
            for balance in balances:
                print(f"  - {balance.coin_type}")
                print(f"    Objects: {balance.coin_object_count}")
                print(f"    Balance: {balance.total_balance}")
                print(f"    Is zero: {balance.is_zero()}")
                print()
            
            # 2. Get SUI balance specifically
            print("2. Getting SUI balance...")
            sui_balance: Balance = await client.coin_query.get_balance(address)
            print(f"SUI Balance: {sui_balance.total_balance}")
            print(f"SUI Objects: {sui_balance.coin_object_count}")
            print()
            
            # 3. Get SUI coin metadata
            print("3. Getting SUI coin metadata...")
            sui_type = "0x2::sui::SUI"
            metadata: SuiCoinMetadata = await client.coin_query.get_coin_metadata(sui_type)
            
            print(f"Name: {metadata.name}")
            print(f"Symbol: {metadata.symbol}")
            print(f"Decimals: {metadata.decimals}")
            print(f"Description: {metadata.description}")
            if metadata.icon_url:
                print(f"Icon: {metadata.icon_url}")
            print()
            
            # 4. Format balance using metadata
            if not sui_balance.is_zero():
                formatted_balance = metadata.format_amount(sui_balance.total_balance_int)
                print(f"Formatted SUI balance: {formatted_balance:.{metadata.decimals}f} {metadata.symbol}")
                print()
            
            # 5. Get paginated coins
            print("4. Getting paginated SUI coins...")
            coins_page: Page[Coin] = await client.coin_query.get_coins(
                address, 
                coin_type=sui_type,
                limit=5
            )
            
            print(f"Page has {len(coins_page)} coins")
            print(f"Has next page: {coins_page.has_next_page}")
            if coins_page.next_cursor:
                print(f"Next cursor: {coins_page.next_cursor}")
            
            for i, coin in enumerate(coins_page):
                print(f"  Coin {i+1}:")
                print(f"    ID: {coin.coin_object_id}")
                print(f"    Balance: {coin.balance}")
                print(f"    Version: {coin.version}")
                print(f"    Previous TX: {coin.previous_transaction}")
                
                # Format coin balance
                formatted_coin_balance = metadata.format_amount(coin.balance_int)
                print(f"    Formatted: {formatted_coin_balance:.{metadata.decimals}f} {metadata.symbol}")
                print()
            
            # 6. Get total supply
            print("5. Getting SUI total supply...")
            supply: Supply = await client.coin_query.get_total_supply(sui_type)
            print(f"Total supply: {supply.value}")
            
            # Format supply using metadata
            formatted_supply = supply.format_with_metadata(metadata)
            print(f"Formatted supply: {formatted_supply:.2f} {metadata.symbol}")
            print()
            
            # 7. Demonstrate pagination
            print("6. Demonstrating pagination...")
            all_coins: Page[Coin] = await client.coin_query.get_all_coins(address, limit=3)
            
            page_count = 1
            current_page = all_coins
            
            while True:
                print(f"Page {page_count}: {len(current_page)} coins")
                
                for coin in current_page:
                    print(f"  - {coin.coin_type}: {coin.balance}")
                
                if not current_page.has_next_page:
                    break
                
                # Get next page
                current_page = await client.coin_query.get_all_coins(
                    address, 
                    cursor=current_page.next_cursor,
                    limit=3
                )
                page_count += 1
                
                # Limit demo to 3 pages
                if page_count > 3:
                    print("  ... (limiting demo to 3 pages)")
                    break
            
            print(f"Total pages processed: {page_count}")
            
        except SuiValidationError as e:
            print(f"Validation error: {e}")
        except SuiRPCError as e:
            print(f"RPC error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def demonstrate_type_safety():
    """Demonstrate type safety features."""
    
    print("\n=== Type Safety Demo ===\n")
    
    try:
        # This will raise a validation error
        invalid_address = SuiAddress.from_str("invalid_address")
    except SuiValidationError as e:
        print(f"✓ Caught invalid address: {e}")
    
    try:
        # This will also raise a validation error
        short_address = SuiAddress.from_str("0x123")
    except SuiValidationError as e:
        print(f"✓ Caught short address: {e}")
    
    # Valid address creation
    valid_address = SuiAddress.from_str(
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )
    print(f"✓ Valid address: {valid_address}")
    
    # Demonstrate Balance methods
    balance_data = {
        "coinType": "0x2::sui::SUI",
        "coinObjectCount": 5,
        "totalBalance": "1000000000",  # 1 SUI in MIST
        "lockedBalance": {}
    }
    
    balance = Balance.from_dict(balance_data)
    print(f"✓ Balance created: {balance.total_balance}")
    print(f"✓ Balance as int: {balance.total_balance_int}")
    print(f"✓ Is zero: {balance.is_zero()}")
    
    # Demonstrate metadata formatting
    metadata_data = {
        "decimals": 9,
        "name": "Sui",
        "symbol": "SUI", 
        "description": "The native token of Sui",
        "id": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    }
    
    metadata = SuiCoinMetadata.from_dict(metadata_data)
    formatted_amount = metadata.format_amount(balance.total_balance_int)
    print(f"✓ Formatted amount: {formatted_amount} {metadata.symbol}")


if __name__ == "__main__":
    print("SuiPy Typed Coin Query API Example")
    print("=" * 40)
    
    # Run the demonstrations
    asyncio.run(demonstrate_typed_coin_queries())
    asyncio.run(demonstrate_type_safety()) 