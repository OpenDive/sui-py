"""
Example usage of the SuiPy Extended API.

This script demonstrates how to use the async Extended API client to:
- Get owned objects for an address
- Query dynamic fields
- Query events and transactions
- Resolve name service addresses
"""

import asyncio
from sui_py import SuiClient, SuiError


async def main():
    """Main example function."""
    
    # Example Sui address (replace with a real address for testing)
    example_address = "0x5584bcfe3e7ce6d77368d753fb9143046171daa59558021b0d07fc336851e8e5"
    
    # Initialize client for testnet
    async with SuiClient("testnet") as client:
        print(f"Connected to: {client.endpoint}")
        print(f"Is connected: {client.is_connected}")
        print()
        
        try:
            # Get owned objects for the address
            print("=== Getting owned objects ===")
            owned_objects = await client.extended_api.get_owned_objects(
                owner=example_address,
                limit=5
            )
            print(f"Has next page: {owned_objects['hasNextPage']}")
            print(f"Number of objects: {len(owned_objects['data'])}")
            
            for obj in owned_objects['data']:
                if 'data' in obj and obj['data']:
                    obj_data = obj['data']
                    print(f"  Object ID: {obj_data.get('objectId', 'N/A')}")
                    print(f"  Type: {obj_data.get('type', 'N/A')}")
                    print(f"  Version: {obj_data.get('version', 'N/A')}")
                    print()
            
            # Query events (example: get all events, limited)
            print("=== Querying events ===")
            try:
                events = await client.extended_api.query_events(
                    query={"All": []},  # Query all events
                    limit=3
                )
                print(f"Has next page: {events['hasNextPage']}")
                print(f"Number of events: {len(events['data'])}")
                
                for event in events['data']:
                    print(f"  Event ID: {event.get('id', {}).get('eventSeq', 'N/A')}")
                    print(f"  Type: {event.get('type', 'N/A')}")
                    print(f"  Package ID: {event.get('packageId', 'N/A')}")
                    print()
            except Exception as e:
                print(f"Event query failed (this is normal if no events): {e}")
                print()
            
            # Query transaction blocks (example: get transactions for an address)
            print("=== Querying transaction blocks ===")
            try:
                transactions = await client.extended_api.query_transaction_blocks(
                    query={"FromAddress": example_address},
                    limit=3
                )
                print(f"Has next page: {transactions['hasNextPage']}")
                print(f"Number of transactions: {len(transactions['data'])}")
                
                for tx in transactions['data']:
                    print(f"  Transaction Digest: {tx.get('digest', 'N/A')}")
                    if 'transaction' in tx and 'data' in tx['transaction']:
                        tx_data = tx['transaction']['data']
                        print(f"  Sender: {tx_data.get('sender', 'N/A')}")
                        print(f"  Gas Budget: {tx_data.get('gasData', {}).get('budget', 'N/A')}")
                    print()
            except Exception as e:
                print(f"Transaction query failed: {e}")
                print()
            
            # Example of dynamic fields (if we have an object with dynamic fields)
            if owned_objects['data']:
                first_object = owned_objects['data'][0]
                if 'data' in first_object and first_object['data']:
                    object_id = first_object['data']['objectId']
                    
                    print(f"=== Getting dynamic fields for object {object_id} ===")
                    try:
                        dynamic_fields = await client.extended_api.get_dynamic_fields(
                            parent_object_id=object_id,
                            limit=5
                        )
                        print(f"Has next page: {dynamic_fields['hasNextPage']}")
                        print(f"Number of dynamic fields: {len(dynamic_fields['data'])}")
                        
                        for field in dynamic_fields['data']:
                            print(f"  Field Name: {field.get('name', 'N/A')}")
                            print(f"  Field Type: {field.get('type', 'N/A')}")
                            print()
                    except Exception as e:
                        print(f"Dynamic fields query failed (object may not have dynamic fields): {e}")
                        print()
            
            # Example of name service resolution
            print("=== Name service resolution ===")
            try:
                # Try to resolve a common name (this might not exist)
                resolved_address = await client.extended_api.resolve_name_service_address("test.sui")
                if resolved_address:
                    print(f"Resolved address for 'test.sui': {resolved_address}")
                else:
                    print("Name 'test.sui' not found")
                
                # Try to get names for our address
                names = await client.extended_api.resolve_name_service_names(
                    address=example_address,
                    limit=5
                )
                print(f"Names for address {example_address}:")
                print(f"Number of names: {len(names['data'])}")
                for name in names['data']:
                    print(f"  Name: {name}")
                print()
            except Exception as e:
                print(f"Name service resolution failed: {e}")
                print()
            
            # Demonstrate subscription methods (will show error message)
            print("=== Subscription methods (not supported in REST client) ===")
            try:
                await client.extended_api.subscribe_events()
            except SuiError as e:
                print(f"Expected error for subscription: {e}")
            
        except SuiError as e:
            print(f"Sui error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 