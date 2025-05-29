"""
Example demonstrating the typed Extended API.

This example shows how to use the SuiPy SDK's Extended API with typed schemas for better
type safety and developer experience.
"""

import asyncio
from typing import List

from sui_py import (
    SuiClient, 
    SuiAddress, 
    ObjectID,
    DynamicFieldInfo, 
    SuiObjectResponse, 
    SuiEvent, 
    SuiTransactionBlockResponse,
    EventFilter, 
    TransactionFilter,
    Page,
    SuiValidationError,
    SuiRPCError
)
from sui_py.constants import NETWORK_ENDPOINTS


async def demonstrate_typed_extended_api():
    """Demonstrate various typed Extended API operations."""
    
    # Initialize client
    async with SuiClient(NETWORK_ENDPOINTS["mainnet"]) as client:
        
        # Example addresses and IDs (replace with real ones for testing)
        address = SuiAddress.from_str("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        object_id = ObjectID.from_str("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        
        try:
            print("=== Typed Extended API Demo ===\n")
            
            # 1. Get dynamic fields with type safety
            print("1. Getting dynamic fields...")
            try:
                dynamic_fields: Page[DynamicFieldInfo] = await client.extended_api.get_dynamic_fields(
                    object_id, 
                    limit=5
                )
                
                print(f"Found {len(dynamic_fields)} dynamic fields:")
                for field in dynamic_fields:
                    print(f"  - Name: {field.name.type} = {field.name.value}")
                    print(f"    Object ID: {field.object_id}")
                    print(f"    Type: {field.type}")
                    print(f"    Version: {field.version}")
                    print()
                
                if dynamic_fields.has_next_page:
                    print(f"Has more pages, next cursor: {dynamic_fields.next_cursor}")
                    
            except SuiRPCError as e:
                print(f"Note: Dynamic fields query failed (expected for demo): {e}")
            print()
            
            # 2. Get owned objects with filtering
            print("2. Getting owned objects...")
            try:
                # Query with type filter
                query_filter = {
                    "StructType": "0x2::coin::Coin<0x2::sui::SUI>"
                }
                
                owned_objects: Page[SuiObjectResponse] = await client.extended_api.get_owned_objects(
                    address,
                    query=query_filter,
                    limit=3
                )
                
                print(f"Found {len(owned_objects)} owned objects:")
                for obj_response in owned_objects:
                    if obj_response.is_success() and obj_response.data:
                        obj_data = obj_response.data
                        print(f"  - Object ID: {obj_data.object_id}")
                        print(f"    Type: {obj_data.type}")
                        print(f"    Version: {obj_data.version}")
                        if obj_data.owner:
                            print(f"    Owner: {obj_data.owner.owner_type}")
                        print()
                    else:
                        print(f"  - Error: {obj_response.error}")
                        
            except SuiRPCError as e:
                print(f"Note: Owned objects query failed (expected for demo): {e}")
            print()
            
            # 3. Query events with filters
            print("3. Querying events...")
            try:
                # Create event filter using helper
                event_filter = EventFilter.by_event_type("0x2::coin::CoinCreated")
                
                events: Page[SuiEvent] = await client.extended_api.query_events(
                    event_filter,
                    limit=5,
                    descending_order=True
                )
                
                print(f"Found {len(events)} events:")
                for event in events:
                    print(f"  - Event ID: {event.id}")
                    print(f"    Package: {event.package_id}")
                    print(f"    Module: {event.transaction_module}")
                    print(f"    Sender: {event.sender}")
                    print(f"    Type: {event.type}")
                    if event.parsed_json:
                        print(f"    Data: {event.parsed_json}")
                    if event.timestamp_ms:
                        print(f"    Timestamp: {event.timestamp_ms}")
                    print()
                    
            except SuiRPCError as e:
                print(f"Note: Events query failed (expected for demo): {e}")
            print()
            
            # 4. Query transactions with filters
            print("4. Querying transactions...")
            try:
                # Create transaction filter using helper
                tx_filter = TransactionFilter.by_from_address(str(address))
                
                transactions: Page[SuiTransactionBlockResponse] = await client.extended_api.query_transaction_blocks(
                    tx_filter,
                    limit=3,
                    descending_order=True
                )
                
                print(f"Found {len(transactions)} transactions:")
                for tx in transactions:
                    print(f"  - Digest: {tx.digest}")
                    if tx.timestamp_ms:
                        print(f"    Timestamp: {tx.timestamp_ms}")
                    if tx.checkpoint:
                        print(f"    Checkpoint: {tx.checkpoint}")
                    if tx.events:
                        print(f"    Events: {len(tx.events)}")
                    if tx.effects:
                        status = tx.effects.get("status", {}).get("status", "unknown")
                        print(f"    Status: {status}")
                    print()
                    
            except SuiRPCError as e:
                print(f"Note: Transactions query failed (expected for demo): {e}")
            print()
            
            # 5. Name service resolution
            print("5. Testing name service...")
            try:
                # Try to resolve a name (this will likely return None for demo)
                resolved_address = await client.extended_api.resolve_name_service_address("example.sui")
                
                if resolved_address:
                    print(f"Resolved address: {resolved_address}")
                else:
                    print("Name not found (expected for demo)")
                
                # Try to resolve names for an address
                names: Page[str] = await client.extended_api.resolve_name_service_names(address)
                
                if len(names) > 0:
                    print(f"Found {len(names)} names for address:")
                    for name in names:
                        print(f"  - {name}")
                else:
                    print("No names found for address (expected for demo)")
                    
            except SuiRPCError as e:
                print(f"Note: Name service query failed (expected for demo): {e}")
            print()
            
            # 6. Demonstrate query filter builders
            print("6. Demonstrating query filter builders...")
            
            # Event filters
            package_filter = EventFilter.by_package("0x2")
            module_filter = EventFilter.by_module("0x2", "coin")
            sender_filter = EventFilter.by_sender(str(address))
            time_filter = EventFilter.by_time_range(1234567890000, 1234567900000)
            
            print("Event filters:")
            print(f"  - By package: {package_filter}")
            print(f"  - By module: {module_filter}")
            print(f"  - By sender: {sender_filter}")
            print(f"  - By time range: {time_filter}")
            print()
            
            # Transaction filters
            checkpoint_filter = TransactionFilter.by_checkpoint(100)
            function_filter = TransactionFilter.by_move_function("0x2", "coin", "transfer")
            input_filter = TransactionFilter.by_input_object(str(object_id))
            
            print("Transaction filters:")
            print(f"  - By checkpoint: {checkpoint_filter}")
            print(f"  - By function: {function_filter}")
            print(f"  - By input object: {input_filter}")
            print()
            
        except SuiValidationError as e:
            print(f"Validation error: {e}")
        except SuiRPCError as e:
            print(f"RPC error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def demonstrate_dynamic_field_operations():
    """Demonstrate dynamic field operations with type safety."""
    
    print("\n=== Dynamic Field Operations Demo ===\n")
    
    async with SuiClient(NETWORK_ENDPOINTS["mainnet"]) as client:
        
        # Example parent object (replace with real one for testing)
        parent_id = ObjectID.from_str("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        
        try:
            # Get dynamic fields
            fields: Page[DynamicFieldInfo] = await client.extended_api.get_dynamic_fields(parent_id)
            
            if len(fields) > 0:
                print(f"Found {len(fields)} dynamic fields:")
                
                for field in fields:
                    print(f"Field: {field.name.type} = {field.name.value}")
                    
                    # Get the actual field object
                    try:
                        field_object: SuiObjectResponse = await client.extended_api.get_dynamic_field_object(
                            parent_id,
                            field.name
                        )
                        
                        if field_object.is_success() and field_object.data:
                            print(f"  Object ID: {field_object.data.object_id}")
                            print(f"  Version: {field_object.data.version}")
                            if field_object.data.content:
                                print(f"  Content: {field_object.data.content}")
                        else:
                            print(f"  Error getting field object: {field_object.error}")
                            
                    except SuiRPCError as e:
                        print(f"  Error: {e}")
                    
                    print()
            else:
                print("No dynamic fields found (expected for demo)")
                
        except SuiRPCError as e:
            print(f"Note: Dynamic field operations failed (expected for demo): {e}")


async def demonstrate_type_safety():
    """Demonstrate type safety features of Extended API."""
    
    print("\n=== Extended API Type Safety Demo ===\n")
    
    try:
        # Test ObjectOwner parsing
        from sui_py.types.extended import ObjectOwner
        
        # Address owner
        address_owner_data = {
            "AddressOwner": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        }
        address_owner = ObjectOwner.from_dict(address_owner_data)
        print(f"✓ Address owner: {address_owner.owner_type} -> {address_owner.address}")
        
        # Object owner
        object_owner_data = {
            "ObjectOwner": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        }
        object_owner = ObjectOwner.from_dict(object_owner_data)
        print(f"✓ Object owner: {object_owner.owner_type} -> {object_owner.object_id}")
        
        # Shared object
        shared_owner_data = {
            "Shared": {"initial_shared_version": 123}
        }
        shared_owner = ObjectOwner.from_dict(shared_owner_data)
        print(f"✓ Shared owner: {shared_owner.owner_type} -> version {shared_owner.initial_shared_version}")
        
        # Immutable
        immutable_owner = ObjectOwner.from_dict("Immutable")
        print(f"✓ Immutable owner: {immutable_owner.owner_type}")
        
        # Test round-trip serialization
        converted = address_owner.to_dict()
        assert converted == address_owner_data
        print("✓ Round-trip serialization works")
        
        # Test filter builders
        event_filter = EventFilter.by_module("0x2", "coin")
        tx_filter = TransactionFilter.by_move_function("0x2", "coin", "transfer")
        print(f"✓ Event filter: {event_filter}")
        print(f"✓ Transaction filter: {tx_filter}")
        
    except Exception as e:
        print(f"✗ Type safety test failed: {e}")


if __name__ == "__main__":
    print("SuiPy Typed Extended API Example")
    print("=" * 40)
    
    # Run the demonstrations
    asyncio.run(demonstrate_typed_extended_api())
    asyncio.run(demonstrate_dynamic_field_operations())
    asyncio.run(demonstrate_type_safety()) 