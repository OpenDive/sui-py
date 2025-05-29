# SuiPy Component Schemas

This document provides an overview of the Component Schemas implementation in SuiPy SDK, which provides type safety and better developer experience when working with Sui blockchain data.

## Overview

Component Schemas are structured data types that correspond directly to the [Sui JSON-RPC API Component Schemas](https://docs.sui.io/sui-api-ref#component-schemas). They transform raw dictionary responses from the Sui API into fully typed Python objects with validation, convenience methods, and serialization support.

## Features

- **Type Safety**: Full type hints and compile-time checking
- **Runtime Validation**: Automatic validation with descriptive error messages
- **Developer Experience**: IDE support, autocomplete, IntelliSense
- **Convenience Methods**: Helper functions for common operations
- **Serialization**: Easy conversion between Python objects and JSON
- **Consistency**: Uniform interface across all API responses

## Implemented Schemas

### Base Types
- `SuiAddress` - Sui blockchain addresses with validation
- `ObjectID` - Sui object identifiers
- `TransactionDigest` - Transaction digests (base58 encoded)
- `Base64` - Base64 encoded data with validation and decoding
- `Hex` - Hexadecimal data with validation and conversion

### Coin Query API Schemas
- `Balance` - Coin balance information with convenience methods
- `Coin` - Individual coin objects with typed fields
- `SuiCoinMetadata` - Metadata with decimal formatting utilities
- `Supply` - Total supply information with formatting methods

### Extended API Schemas
- `DynamicFieldName` - Dynamic field names with type and value
- `DynamicFieldInfo` - Dynamic field information
- `ObjectOwner` - Object ownership (Address, Object, Shared, Immutable)
- `SuiObjectData` - Complete object data with optional fields
- `SuiObjectResponse` - Object responses with success/error handling
- `SuiEvent` - Blockchain events with parsed data
- `SuiTransactionBlock` - Transaction blocks with data and signatures
- `SuiTransactionBlockResponse` - Complete transaction responses

### Utility Types
- `Page[T]` - Generic paginated response wrapper
- `EventFilter` - Helper for building event query filters
- `TransactionFilter` - Helper for building transaction query filters

## Quick Start

```python
from sui_py import SuiClient, SuiAddress, EventFilter

async with SuiClient("https://fullnode.mainnet.sui.io:443") as client:
    # Type-safe address creation with validation
    address = SuiAddress.from_str("0x...")
    
    # Coin Query API - returns typed objects
    balances = await client.coin_query.get_all_balances(address)
    for balance in balances:
        if not balance.is_zero():
            print(f"{balance.coin_type}: {balance.total_balance}")
    
    # Extended API - returns typed objects
    event_filter = EventFilter.by_package("0x2")
    events = await client.extended_api.query_events(event_filter, limit=10)
    for event in events:
        print(f"Event: {event.type} from {event.sender}")
```

## Benefits

### Before (Raw Dictionaries)
```python
# No type safety, prone to errors
balance_data = await client.coin_query.get_balance(address)
total = int(balance_data["totalBalance"])  # Manual conversion
if total == 0:  # Manual zero check
    print("No balance")
```

### After (Typed Schemas)
```python
# Type-safe with validation and convenience methods
balance = await client.coin_query.get_balance(address)
total = balance.total_balance_int  # Automatic conversion
if balance.is_zero():  # Convenience method
    print("No balance")
```

## Documentation

- [Coin Query API Schemas](coin_query_schemas.md) - Complete documentation for coin-related types
- [Extended API Schemas](extended_api_schemas.md) - Complete documentation for extended API types

## Examples

- [Typed Coin Query Example](../examples/typed_coin_query_example.py) - Demonstrates coin API with type safety
- [Typed Extended API Example](../examples/typed_extended_api_example.py) - Demonstrates extended API with type safety

## Testing

Comprehensive test suites ensure reliability:

```bash
# Test coin schemas
python -m pytest tests/test_coin_schemas.py -v

# Test extended schemas  
python -m pytest tests/test_extended_schemas.py -v

# Test all schemas
python -m pytest tests/ -v
```

## Migration Guide

### From Raw Dictionaries

If you're upgrading from raw dictionary responses, the migration is straightforward:

```python
# Old way
balance_dict = await client.coin_query.get_balance(address)
total = balance_dict["totalBalance"]
coin_type = balance_dict["coinType"]

# New way (backward compatible)
balance = await client.coin_query.get_balance(address)
total = balance.total_balance  # or balance.total_balance_int for int
coin_type = balance.coin_type

# Convert back to dict if needed
balance_dict = balance.to_dict()
```

### Type Annotations

Add type annotations to get full IDE support:

```python
from sui_py import Balance, Page, SuiEvent
from typing import List

# Function signatures with types
async def process_balances(address: SuiAddress) -> List[Balance]:
    return await client.coin_query.get_all_balances(address)

async def process_events(filter_dict: Dict[str, Any]) -> Page[SuiEvent]:
    return await client.extended_api.query_events(filter_dict)
```

## Error Handling

Schemas provide clear error messages for validation failures:

```python
try:
    address = SuiAddress.from_str("invalid")
except SuiValidationError as e:
    print(f"Invalid address: {e}")
    # Output: Invalid address: Invalid Sui address format: invalid. Expected 32-byte hex string with 0x prefix (66 characters total)
```

## Performance

- **Minimal Overhead**: Schemas add negligible performance cost
- **Lazy Validation**: Validation only occurs during object creation
- **Memory Efficient**: Uses dataclasses with `frozen=True` for immutability
- **Caching**: Base types can be reused across multiple objects

## Future Extensions

The schema system is designed to be easily extensible:

1. **Additional APIs**: New Sui API endpoints can easily add their own schemas
2. **Custom Validation**: Add domain-specific validation rules
3. **Serialization Formats**: Support for additional formats (CBOR, MessagePack, etc.)
4. **Performance Optimizations**: Optional fast-path parsing for high-throughput scenarios

## Contributing

When adding new schemas:

1. Follow the existing patterns in `sui_py/types/`
2. Add comprehensive tests in `tests/`
3. Update documentation and examples
4. Ensure backward compatibility with raw dictionary access

The Component Schemas provide a solid foundation for type-safe Sui blockchain development while maintaining the flexibility and performance of the underlying SDK. 