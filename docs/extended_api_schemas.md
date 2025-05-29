# Extended API Component Schemas

This document describes the typed Component Schemas implemented for the SuiPy SDK's Extended API. These schemas provide type safety, validation, and better developer experience when working with dynamic fields, objects, events, and transactions from the Sui blockchain.

## Overview

The Extended API Component Schemas correspond directly to the [Sui JSON-RPC Extended API Component Schemas](https://docs.sui.io/sui-api-ref#extended-api). They provide:

- **Type Safety**: Compile-time and runtime type checking for complex data structures
- **Validation**: Automatic validation of addresses, object IDs, and other blockchain identifiers
- **Developer Experience**: IDE support, autocomplete, and clear error messages
- **Query Helpers**: Convenient filter builders for events and transactions
- **Serialization**: Easy conversion between Python objects and JSON

## Dynamic Field Types

### DynamicFieldName
Represents a dynamic field name with type and value.

```python
from sui_py import DynamicFieldName

# Create from API response
name_data = {
    "type": "0x1::string::String",
    "value": "my_field"
}

field_name = DynamicFieldName.from_dict(name_data)
print(f"Type: {field_name.type}")
print(f"Value: {field_name.value}")

# Convert back to dict
dict_data = field_name.to_dict()
```

### DynamicFieldInfo
Represents information about a dynamic field.

```python
from sui_py import DynamicFieldInfo

field_info_data = {
    "name": {
        "type": "u64",
        "value": 42
    },
    "bcsName": "0x2a",
    "type": "DynamicField",
    "objectType": "0x2::dynamic_field::Field<u64, 0x1::string::String>",
    "objectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "version": 1,
    "digest": "abc123"
}

field_info = DynamicFieldInfo.from_dict(field_info_data)

# Typed access
print(f"Field name: {field_info.name.type} = {field_info.name.value}")
print(f"Object ID: {field_info.object_id}")  # ObjectID type
print(f"Version: {field_info.version}")
```

## Object Types

### ObjectOwner
Represents object ownership information with support for different ownership types.

```python
from sui_py.types.extended import ObjectOwner

# Address owner
address_owner_data = {
    "AddressOwner": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
}
address_owner = ObjectOwner.from_dict(address_owner_data)
print(f"Owner type: {address_owner.owner_type}")
print(f"Address: {address_owner.address}")  # SuiAddress type

# Object owner
object_owner_data = {
    "ObjectOwner": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
}
object_owner = ObjectOwner.from_dict(object_owner_data)
print(f"Object ID: {object_owner.object_id}")  # ObjectID type

# Shared object
shared_data = {
    "Shared": {"initial_shared_version": 123}
}
shared_owner = ObjectOwner.from_dict(shared_data)
print(f"Initial version: {shared_owner.initial_shared_version}")

# Immutable object
immutable_owner = ObjectOwner.from_dict("Immutable")
print(f"Owner type: {immutable_owner.owner_type}")
```

### SuiObjectData
Represents complete object data with optional fields.

```python
from sui_py import SuiObjectData

object_data = {
    "objectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "version": 1,
    "digest": "abc123",
    "type": "0x2::coin::Coin<0x2::sui::SUI>",
    "owner": {
        "AddressOwner": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    },
    "previousTransaction": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
    "storageRebate": 100,
    "content": {
        "dataType": "moveObject",
        "type": "0x2::coin::Coin<0x2::sui::SUI>",
        "hasPublicTransfer": True,
        "fields": {
            "balance": "1000000000",
            "id": {"id": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"}
        }
    }
}

obj_data = SuiObjectData.from_dict(object_data)

# Typed access
print(f"Object ID: {obj_data.object_id}")  # ObjectID type
print(f"Owner: {obj_data.owner.owner_type}")  # ObjectOwner type
print(f"Previous TX: {obj_data.previous_transaction}")  # TransactionDigest type
```

### SuiObjectResponse
Represents an object response that may contain data or an error.

```python
from sui_py import SuiObjectResponse

# Successful response
success_data = {
    "data": {
        "objectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "version": 1,
        "digest": "abc123"
    }
}

response = SuiObjectResponse.from_dict(success_data)
if response.is_success():
    print(f"Object: {response.data.object_id}")
else:
    print(f"Error: {response.error}")

# Error response
error_data = {
    "error": {
        "code": "objectNotFound",
        "message": "Object not found"
    }
}

error_response = SuiObjectResponse.from_dict(error_data)
print(f"Success: {error_response.is_success()}")  # False
```

## Event Types

### SuiEvent
Represents a blockchain event with parsed data.

```python
from sui_py import SuiEvent

event_data = {
    "id": {
        "txDigest": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
        "eventSeq": "0"
    },
    "packageId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "transactionModule": "coin",
    "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "type": "0x2::coin::CoinCreated<0x2::sui::SUI>",
    "parsedJson": {
        "amount": "1000000000",
        "owner": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    },
    "timestampMs": 1234567890000
}

event = SuiEvent.from_dict(event_data)

# Typed access
print(f"Package: {event.package_id}")  # ObjectID type
print(f"Sender: {event.sender}")  # SuiAddress type
print(f"Type: {event.type}")
print(f"Data: {event.parsed_json}")
print(f"Timestamp: {event.timestamp_ms}")
```

## Transaction Types

### SuiTransactionBlock
Represents a transaction block with data and signatures.

```python
from sui_py import SuiTransactionBlock

tx_data = {
    "data": {
        "messageVersion": "v1",
        "transaction": {
            "kind": "ProgrammableTransaction",
            "inputs": [],
            "transactions": []
        },
        "sender": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "gasData": {
            "payment": [],
            "owner": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "price": "1000",
            "budget": "1000000"
        }
    },
    "txSignatures": ["signature1", "signature2"]
}

tx_block = SuiTransactionBlock.from_dict(tx_data)
print(f"Signatures: {len(tx_block.tx_signatures)}")
print(f"Transaction data: {tx_block.data}")
```

### SuiTransactionBlockResponse
Represents a complete transaction response with effects and events.

```python
from sui_py import SuiTransactionBlockResponse

tx_response_data = {
    "digest": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
    "transaction": {
        "data": {"messageVersion": "v1"},
        "txSignatures": ["sig1"]
    },
    "effects": {
        "messageVersion": "v1",
        "status": {"status": "success"},
        "executedEpoch": "0"
    },
    "events": [
        {
            "id": {"txDigest": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF", "eventSeq": "0"},
            "packageId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "transactionModule": "test",
            "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "type": "test::Event"
        }
    ],
    "timestampMs": 1234567890000,
    "checkpoint": 100
}

tx_response = SuiTransactionBlockResponse.from_dict(tx_response_data)

# Typed access
print(f"Digest: {tx_response.digest}")  # TransactionDigest type
print(f"Events: {len(tx_response.events)}")  # List[SuiEvent]
print(f"Checkpoint: {tx_response.checkpoint}")
print(f"Status: {tx_response.effects['status']['status']}")
```

## Query Filter Helpers

### EventFilter
Helper class for building event query filters.

```python
from sui_py import EventFilter

# Filter by package
package_filter = EventFilter.by_package("0x2")
# Result: {"Package": "0x2"}

# Filter by module
module_filter = EventFilter.by_module("0x2", "coin")
# Result: {"MoveModule": {"package": "0x2", "module": "coin"}}

# Filter by event type
type_filter = EventFilter.by_event_type("0x2::coin::CoinCreated")
# Result: {"MoveEventType": "0x2::coin::CoinCreated"}

# Filter by sender
sender_filter = EventFilter.by_sender("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
# Result: {"Sender": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"}

# Filter by transaction
tx_filter = EventFilter.by_transaction("9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF")
# Result: {"Transaction": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF"}

# Filter by time range
time_filter = EventFilter.by_time_range(1234567890000, 1234567900000)
# Result: {"TimeRange": {"start_time": 1234567890000, "end_time": 1234567900000}}
```

### TransactionFilter
Helper class for building transaction query filters.

```python
from sui_py import TransactionFilter

# Filter by checkpoint
checkpoint_filter = TransactionFilter.by_checkpoint(100)
# Result: {"Checkpoint": 100}

# Filter by Move function call
function_filter = TransactionFilter.by_move_function("0x2", "coin", "transfer")
# Result: {"MoveFunction": {"package": "0x2", "module": "coin", "function": "transfer"}}

# Filter by input object
input_filter = TransactionFilter.by_input_object("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
# Result: {"InputObject": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"}

# Filter by changed object
changed_filter = TransactionFilter.by_changed_object("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
# Result: {"ChangedObject": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"}

# Filter by sender address
from_filter = TransactionFilter.by_from_address("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
# Result: {"FromAddress": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"}

# Filter by recipient address
to_filter = TransactionFilter.by_to_address("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
# Result: {"ToAddress": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"}
```

## Updated Extended API Client

The `ExtendedAPIClient` now returns typed objects instead of raw dictionaries:

```python
from sui_py import SuiClient, SuiAddress, ObjectID, EventFilter, TransactionFilter

async with SuiClient("https://fullnode.mainnet.sui.io:443") as client:
    address = SuiAddress.from_str("0x...")
    object_id = ObjectID.from_str("0x...")
    
    # Returns Page[DynamicFieldInfo] instead of Dict
    dynamic_fields = await client.extended_api.get_dynamic_fields(object_id, limit=10)
    
    # Returns Page[SuiObjectResponse] instead of Dict
    owned_objects = await client.extended_api.get_owned_objects(address, limit=10)
    
    # Returns Page[SuiEvent] instead of Dict
    event_filter = EventFilter.by_package("0x2")
    events = await client.extended_api.query_events(event_filter, limit=10)
    
    # Returns Page[SuiTransactionBlockResponse] instead of Dict
    tx_filter = TransactionFilter.by_from_address(str(address))
    transactions = await client.extended_api.query_transaction_blocks(tx_filter, limit=10)
    
    # Returns Optional[SuiAddress] instead of Optional[str]
    resolved_address = await client.extended_api.resolve_name_service_address("example.sui")
    
    # Type-safe operations
    for field in dynamic_fields:
        print(f"Field: {field.name.type} = {field.name.value}")
        print(f"Object: {field.object_id}")
    
    for obj_response in owned_objects:
        if obj_response.is_success() and obj_response.data:
            print(f"Object: {obj_response.data.object_id}")
            print(f"Type: {obj_response.data.type}")
    
    for event in events:
        print(f"Event: {event.type}")
        print(f"Sender: {event.sender}")
        print(f"Package: {event.package_id}")
    
    for tx in transactions:
        print(f"Transaction: {tx.digest}")
        if tx.events:
            print(f"Events: {len(tx.events)}")
```

## Benefits

1. **Type Safety**: Catch errors at development time with proper type hints
2. **Validation**: Automatic validation of addresses, object IDs, and other blockchain identifiers
3. **IDE Support**: Full autocomplete and IntelliSense support for complex nested structures
4. **Error Handling**: Clear distinction between successful responses and errors
5. **Query Helpers**: Convenient filter builders reduce boilerplate code
6. **Consistency**: Uniform interface across all Extended API responses
7. **Future-Proof**: Easy to extend with additional validation and methods

## Testing

Comprehensive tests are included in `tests/test_extended_schemas.py` covering:

- Dynamic field types and operations
- Object types and ownership models
- Event parsing and validation
- Transaction response handling
- Query filter builders
- Round-trip serialization
- Pagination with typed objects
- Error handling

Run tests with:
```bash
python -m pytest tests/test_extended_schemas.py -v
```

## Examples

See `examples/typed_extended_api_example.py` for a complete demonstration of the typed Extended API in action, including:

- Dynamic field operations
- Object queries with filters
- Event queries with various filters
- Transaction queries
- Name service resolution
- Query filter builders
- Type safety demonstrations
- Error handling patterns 