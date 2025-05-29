"""
Example usage of the SuiPy Coin Query API.

This script demonstrates how to use the async Coin Query client to:
- Get all balances for an address
- Get specific coin balances
- Query coin metadata
- Paginate through coin objects
"""

import asyncio
from sui_py import SuiClient, SuiError


async def main():
    """Main example function."""
    
    # Example Sui address (replace with a real address for testing)
    example_address = "0x94f1a597b4e8f709a396f7f6b1482bdcd65a673d111e49286c527fab7c2d0961"
    
    # Initialize client for mainnet
    async with SuiClient("mainnet") as client:
        print(f"Connected to: {client.endpoint}")
        print(f"Is connected: {client.is_connected}")
        print()
        
        try:
            # Get all balances for the address
            print("=== Getting all balances ===")
            balances = await client.coin_query.get_all_balances(example_address)
            for balance in balances:
                print(f"Coin Type: {balance['coinType']}")
                print(f"Total Balance: {balance['totalBalance']}")
                print(f"Coin Count: {balance['coinObjectCount']}")
                print()
            
            # Get SUI balance specifically
            print("=== Getting SUI balance ===")
            sui_balance = await client.coin_query.get_balance(example_address)
            print(f"SUI Balance: {sui_balance['totalBalance']}")
            print(f"SUI Coin Count: {sui_balance['coinObjectCount']}")
            print()
            
            # Get SUI coin metadata
            print("=== Getting SUI metadata ===")
            sui_metadata = await client.coin_query.get_coin_metadata("0x2::sui::SUI")
            print(f"Name: {sui_metadata['name']}")
            print(f"Symbol: {sui_metadata['symbol']}")
            print(f"Decimals: {sui_metadata['decimals']}")
            print(f"Description: {sui_metadata['description']}")
            print()
            
            # Get all coins with pagination
            print("=== Getting all coins (first 3) ===")
            coins_page = await client.coin_query.get_all_coins(
                owner=example_address,
                limit=3
            )
            print(f"Has next page: {coins_page['hasNextPage']}")
            print(f"Number of coins: {len(coins_page['data'])}")
            
            for coin in coins_page['data']:
                print(f"  Coin ID: {coin['coinObjectId']}")
                print(f"  Balance: {coin['balance']}")
                print(f"  Type: {coin['coinType']}")
                print()
            
            # Get total supply of SUI
            print("=== Getting SUI total supply ===")
            supply = await client.coin_query.get_total_supply("0x2::sui::SUI")
            print(f"Total SUI Supply: {supply['value']}")
            
        except SuiError as e:
            print(f"Sui error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 