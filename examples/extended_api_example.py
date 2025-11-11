"""
Comprehensive example of the SuiPy Extended API.

This script demonstrates how to use the async Extended API client for:

BASIC OPERATIONS:
- Get owned objects for an address
- Query dynamic fields and field objects
- Query events and transactions
- Resolve name service addresses

ADVANCED FEATURES:
- Type-safe operations with explicit typing
- Query filter builders and advanced filtering
- Comprehensive error handling
- Type safety demonstrations
- Real-world usage patterns
"""

import asyncio
from typing import List

from sui_py import (
    SuiClient, SuiError, SuiValidationError, SuiRPCError,
    SuiAddress, ObjectID, DynamicFieldInfo, SuiObjectResponse, 
    SuiEvent, SuiTransactionBlockResponse, EventFilter, 
    TransactionFilter, Page
)


async def basic_extended_operations():
    """Demonstrate basic Extended API operations."""
    
    print("🔹 BASIC EXTENDED API OPERATIONS")
    print("=" * 50)
    
    # Use mainnet for better data availability
    async with SuiClient("mainnet") as client:
        print(f"Connected to: {client.endpoint}")
        print()
        
        # Use a well-known address with activity
        example_address = "0x5584bcfe3e7ce6d77368d753fb9143046171daa59558021b0d07fc336851e8e5"
        
        try:
            # Get owned objects for the address
            print("=== Getting owned objects ===")
            owned_objects: Page[SuiObjectResponse] = await client.extended_api.get_owned_objects(
                owner=example_address,
                limit=5
            )
            print(f"Has next page: {owned_objects.has_next_page}")
            print(f"Number of objects: {len(owned_objects.data)}")
            
            for obj_response in owned_objects.data:
                if obj_response.is_success() and obj_response.data:
                    obj_data = obj_response.data
                    print(f"  • Object ID: {obj_data.object_id}")
                    print(f"    Type: {obj_data.type}")
                    print(f"    Version: {obj_data.version}")
                    if obj_data.owner:
                        print(f"    Owner: {obj_data.owner.owner_type}")
                    print()
                else:
                    print(f"  • Error: {obj_response.error}")
                    print()
            
            # Query events (example: get recent events)
            print("=== Querying recent events ===")
            try:
                events: Page[SuiEvent] = await client.extended_api.query_events(
                    query={"All": []},  # Query all events
                    limit=3,
                    descending_order=True
                )
                print(f"Has next page: {events.has_next_page}")
                print(f"Number of events: {len(events.data)}")
                
                for event in events.data:
                    print(f"  • Event ID: {event.id}")
                    print(f"    Type: {event.type}")
                    print(f"    Package: {event.package_id}")
                    print(f"    Sender: {event.sender}")
                    if event.timestamp_ms:
                        print(f"    Timestamp: {event.timestamp_ms}")
                    print()
            except SuiRPCError as e:
                print(f"Event query failed: {e}")
                print()
            
            # Query transaction blocks
            print("=== Querying transaction blocks ===")
            try:
                tx_filter = TransactionFilter.by_from_address(example_address)
                transactions: Page[SuiTransactionBlockResponse] = await client.extended_api.query_transaction_blocks(
                    query=tx_filter,
                    limit=3,
                    descending_order=True
                )
                print(f"Has next page: {transactions.has_next_page}")
                print(f"Number of transactions: {len(transactions.data)}")
                
                for tx in transactions.data:
                    print(f"  • Transaction Digest: {tx.digest}")
                    if tx.timestamp_ms:
                        print(f"    Timestamp: {tx.timestamp_ms}")
                    if tx.checkpoint:
                        print(f"    Checkpoint: {tx.checkpoint}")
                    if tx.effects and hasattr(tx.effects, 'status'):
                        print(f"    Status: {tx.effects.status}")
                    print()
            except SuiRPCError as e:
                print(f"Transaction query failed: {e}")
                print()
            
            # Example of dynamic fields (if we have an object with dynamic fields)
            if owned_objects.data:
                first_object = owned_objects.data[0]
                if first_object.is_success() and first_object.data:
                    object_id = first_object.data.object_id
                    
                    print(f"=== Getting dynamic fields for object {object_id} ===")
                    try:
                        dynamic_fields: Page[DynamicFieldInfo] = await client.extended_api.get_dynamic_fields(
                            parent_object_id=object_id,
                            limit=5
                        )
                        print(f"Has next page: {dynamic_fields.has_next_page}")
                        print(f"Number of dynamic fields: {len(dynamic_fields.data)}")
                        
                        for field in dynamic_fields.data:
                            print(f"  • Field Name: {field.name.type} = {field.name.value}")
                            print(f"    Object ID: {field.object_id}")
                            print(f"    Type: {field.type}")
                            print(f"    Version: {field.version}")
                            print()
                    except SuiRPCError as e:
                        print(f"Dynamic fields query failed (object may not have dynamic fields): {e}")
                        print()
            
            # Example of name service resolution
            print("=== Name service resolution ===")
            try:
                # Try to resolve a common name
                resolved_address = await client.extended_api.resolve_name_service_address("example.sui")
                if resolved_address:
                    print(f"Resolved address for 'example.sui': {resolved_address}")
                else:
                    print("Name 'example.sui' not found (expected)")
                
                # Try to get names for our address
                names: Page[str] = await client.extended_api.resolve_name_service_names(
                    address=example_address,
                    limit=5
                )
                print(f"Names for address {example_address}:")
                print(f"Number of names: {len(names.data)}")
                for name in names.data:
                    print(f"  • Name: {name}")
                print()
            except SuiRPCError as e:
                print(f"Name service resolution failed: {e}")
                print()
            
        except SuiRPCError as e:
            print(f"RPC error occurred: {e}")
        except SuiError as e:
            print(f"Sui error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def advanced_extended_operations():
    """Demonstrate advanced Extended API features."""
    
    print("🔸 ADVANCED EXTENDED API OPERATIONS")
    print("=" * 50)
    
    async with SuiClient("mainnet") as client:
        
        # Use typed addresses for better validation
        example_address = SuiAddress.from_str("0x5584bcfe3e7ce6d77368d753fb9143046171daa59558021b0d07fc336851e8e5")
        
        try:
            # Demonstrate query filter builders
            print("=== Query filter demonstrations ===")
            
            # Event filters
            package_filter = EventFilter.by_package("0x2")
            module_filter = EventFilter.by_module("0x2", "coin")
            sender_filter = EventFilter.by_sender(str(example_address))
            event_type_filter = EventFilter.by_event_type("0x2::coin::CoinCreated")
            
            print("Event filters:")
            print(f"  • By package: {package_filter}")
            print(f"  • By module: {module_filter}")
            print(f"  • By sender: {sender_filter}")
            print(f"  • By event type: {event_type_filter}")
            print()
            
            # Transaction filters
            checkpoint_filter = TransactionFilter.by_checkpoint(1000)
            function_filter = TransactionFilter.by_move_function("0x2", "coin", "transfer")
            
            print("Transaction filters:")
            print(f"  • By checkpoint: {checkpoint_filter}")
            print(f"  • By function: {function_filter}")
            print()
            
            # Demonstrate filtered queries
            print("=== Filtered event queries ===")
            try:
                # Query coin-related events
                coin_events: Page[SuiEvent] = await client.extended_api.query_events(
                    query=module_filter,
                    limit=5,
                    descending_order=True
                )
                
                print(f"Found {len(coin_events.data)} coin-related events:")
                for event in coin_events.data:
                    print(f"  • {event.type}")
                    print(f"    Package: {event.package_id}")
                    print(f"    Sender: {event.sender}")
                    if event.parsed_json:
                        print(f"    Data: {event.parsed_json}")
                    print()
                    
            except SuiRPCError as e:
                print(f"Filtered events query failed: {e}")
            print()
            
            # Demonstrate object filtering
            print("=== Filtered object queries ===")
            try:
                # Query for SUI coin objects
                sui_coin_filter = {
                    "StructType": "0x2::coin::Coin<0x2::sui::SUI>"
                }
                
                sui_coins: Page[SuiObjectResponse] = await client.extended_api.get_owned_objects(
                    owner=example_address,
                    query=sui_coin_filter,
                    limit=3
                )
                
                print(f"Found {len(sui_coins.data)} SUI coin objects:")
                for obj_response in sui_coins.data:
                    if obj_response.is_success() and obj_response.data:
                        obj_data = obj_response.data
                        print(f"  • Object ID: {obj_data.object_id}")
                        print(f"    Version: {obj_data.version}")
                        if obj_data.content and hasattr(obj_data.content, 'fields'):
                            print(f"    Balance: {obj_data.content.fields.get('balance', 'N/A')}")
                        print()
                        
            except SuiRPCError as e:
                print(f"Filtered objects query failed: {e}")
            print()
            
            # Demonstrate dynamic field operations
            print("=== Dynamic field operations ===")
            try:
                # Use a known object with dynamic fields (if available)
                test_object_id = ObjectID.from_str("0x0000000000000000000000000000000000000000000000000000000000000005")
                
                fields: Page[DynamicFieldInfo] = await client.extended_api.get_dynamic_fields(
                    parent_object_id=test_object_id,
                    limit=3
                )
                
                if len(fields.data) > 0:
                    print(f"Found {len(fields.data)} dynamic fields:")
                    
                    for field in fields.data:
                        print(f"  • Field: {field.name.type} = {field.name.value}")
                        
                        # Get the actual field object
                        try:
                            field_object: SuiObjectResponse = await client.extended_api.get_dynamic_field_object(
                                parent_object_id=test_object_id,
                                name=field.name
                            )
                            
                            if field_object.is_success() and field_object.data:
                                print(f"    Object ID: {field_object.data.object_id}")
                                print(f"    Version: {field_object.data.version}")
                            else:
                                print(f"    Error: {field_object.error}")
                                
                        except SuiRPCError as e:
                            print(f"    Error getting field object: {e}")
                        print()
                else:
                    print("No dynamic fields found (expected for demo object)")
                    
            except SuiRPCError as e:
                print(f"Dynamic field operations failed: {e}")
            print()
            
        except SuiValidationError as e:
            print(f"Validation error: {e}")
        except SuiRPCError as e:
            print(f"RPC error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def demonstrate_type_safety():
    """Demonstrate type safety features of Extended API."""
    
    print("🔷 TYPE SAFETY DEMONSTRATION")
    print("=" * 50)
    
    try:
        # Test address validation
        print("=== Address validation ===")
        
        try:
            invalid_address = SuiAddress.from_str("invalid_address")
            print(f"❌ Unexpected success: {invalid_address}")
        except SuiValidationError as e:
            print(f"✅ Caught invalid address: {e}")
        
        valid_address = SuiAddress.from_str("0x5584bcfe3e7ce6d77368d753fb9143046171daa59558021b0d07fc336851e8e5")
        print(f"✅ Valid address: {valid_address}")
        print()
        
        # Test ObjectID validation
        print("=== ObjectID validation ===")
        
        try:
            invalid_object_id = ObjectID.from_str("invalid_object_id")
            print(f"❌ Unexpected success: {invalid_object_id}")
        except SuiValidationError as e:
            print(f"✅ Caught invalid object ID: {e}")
        
        valid_object_id = ObjectID.from_str("0x0000000000000000000000000000000000000000000000000000000000000005")
        print(f"✅ Valid object ID: {valid_object_id}")
        print()
        
        # Test filter builders
        print("=== Filter builder validation ===")
        
        # Event filters
        event_filter = EventFilter.by_module("0x2", "coin")
        print(f"✅ Event filter: {event_filter}")
        
        # Transaction filters
        tx_filter = TransactionFilter.by_move_function("0x2", "coin", "transfer")
        print(f"✅ Transaction filter: {tx_filter}")
        
        # Time range filter
        time_filter = EventFilter.by_time_range(1234567890000, 1234567900000)
        print(f"✅ Time range filter: {time_filter}")
        print()
        
        # Test ObjectOwner type handling
        print("=== ObjectOwner type handling ===")
        from sui_py.types.extended import ObjectOwner
        
        # Address owner
        address_owner_data = {
            "AddressOwner": "0x5584bcfe3e7ce6d77368d753fb9143046171daa59558021b0d07fc336851e8e5"
        }
        address_owner = ObjectOwner.from_dict(address_owner_data)
        print(f"✅ Address owner: {address_owner.owner_type} -> {address_owner.address}")
        
        # Shared object
        shared_owner_data = {
            "Shared": {"initial_shared_version": 123}
        }
        shared_owner = ObjectOwner.from_dict(shared_owner_data)
        print(f"✅ Shared owner: {shared_owner.owner_type} -> version {shared_owner.initial_shared_version}")
        
        # Test round-trip serialization
        converted = address_owner.to_dict()
        assert converted == address_owner_data
        print("✅ Round-trip serialization works")
        print()
        
    except Exception as e:
        print(f"❌ Type safety test failed: {e}")


async def main():
    """Main example function that runs all demonstrations."""
    
    print("SuiPy Comprehensive Extended API Example")
    print("=" * 60)
    print()
    
    # Run basic operations
    await basic_extended_operations()
    print("\n" + "=" * 60 + "\n")
    
    # Run advanced operations  
    await advanced_extended_operations()
    print("\n" + "=" * 60 + "\n")
    
    # Run type safety demonstration
    await demonstrate_type_safety()


if __name__ == "__main__":
    asyncio.run(main()) 