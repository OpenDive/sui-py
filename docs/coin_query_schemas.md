# Coin Query API Component Schemas

This document describes the typed Component Schemas implemented for the SuiPy SDK's Coin Query API. These schemas provide type safety, validation, and better developer experience when working with coin-related data from the Sui blockchain.

## Overview

The Component Schemas are structured data types that correspond directly to the [Sui JSON-RPC API Component Schemas](https://docs.sui.io/sui-api-ref#component-schemas). They provide:

- **Type Safety**: Compile-time and runtime type checking
- **Validation**: Automatic validation of data formats (addresses, object IDs, etc.)
- **Developer Experience**: IDE support, autocomplete, and clear error messages
- **Serialization**: Easy conversion between Python objects and JSON

## Base Types

### SuiAddress
Represents a Sui blockchain address with validation.

```python
from sui_py import SuiAddress

# Create from string with validation
address = SuiAddress.from_str("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")

# Automatic validation
try:
    invalid = SuiAddress.from_str("invalid_address")
except SuiValidationError as e:
    print(f"Validation failed: {e}")
```

**Format**: 32-byte hex string with `0x` prefix (66 characters total)

### ObjectID
Represents a Sui object identifier with the same format as addresses.

```python
from sui_py import ObjectID

obj_id = ObjectID.from_str("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
```

### TransactionDigest
Represents a transaction digest (base58 encoded).

```python
from sui_py import TransactionDigest

digest = TransactionDigest.from_str("9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF")
```

### Base64 and Hex
Utility types for base64 and hexadecimal data with validation.

```python
from sui_py import Base64, Hex

# Base64 with validation and decoding
b64 = Base64.from_str("SGVsbG8gV29ybGQ=")
decoded = b64.decode()  # Returns bytes

# Hex with validation and conversion
hex_data = Hex.from_str("0x48656c6c6f")
bytes_data = hex_data.to_bytes()
```

## Coin Types

### Balance
Represents coin balance information for an address.

```python
from sui_py import Balance

# From API response
balance_data = {
    "coinType": "0x2::sui::SUI",
    "coinObjectCount": 5,
    "totalBalance": "1000000000",
    "lockedBalance": {}
}

balance = Balance.from_dict(balance_data)

# Convenient methods
print(f"Balance: {balance.total_balance}")
print(f"As integer: {balance.total_balance_int}")
print(f"Is zero: {balance.is_zero()}")

# Convert back to dict
dict_data = balance.to_dict()
```

### Coin
Represents an individual coin object.

```python
from sui_py import Coin

coin_data = {
    "coinType": "0x2::sui::SUI",
    "coinObjectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "version": "123",
    "digest": "abc123",
    "balance": "500000000",
    "previousTransaction": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF"
}

coin = Coin.from_dict(coin_data)

# Typed access
print(f"Object ID: {coin.coin_object_id}")  # ObjectID type
print(f"Balance: {coin.balance_int}")       # Converted to int
print(f"Previous TX: {coin.previous_transaction}")  # TransactionDigest type
```

### SuiCoinMetadata
Represents metadata for a coin type with formatting utilities.

```python
from sui_py import SuiCoinMetadata

metadata_data = {
    "decimals": 9,
    "name": "Sui",
    "symbol": "SUI",
    "description": "The native token of Sui",
    "iconUrl": "https://example.com/sui.png",
    "id": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
}

metadata = SuiCoinMetadata.from_dict(metadata_data)

# Format amounts using decimal places
raw_amount = 1000000000  # 1 SUI in MIST
formatted = metadata.format_amount(raw_amount)  # 1.0

# Parse formatted amounts back to raw
parsed = metadata.parse_amount(1.5)  # 1500000000
```

### Supply
Represents total supply information for a coin type.

```python
from sui_py import Supply

supply_data = {"value": "10000000000000000000"}
supply = Supply.from_dict(supply_data)

# Format with metadata
formatted_supply = supply.format_with_metadata(metadata)
print(f"Total supply: {formatted_supply:.2f} {metadata.symbol}")
```

## Pagination

### Page[T]
Generic paginated response wrapper for any data type.

```python
from sui_py import Page, Coin

# From API response
response_data = {
    "data": [coin_data1, coin_data2, coin_data3],
    "hasNextPage": True,
    "nextCursor": "cursor123"
}

# Parse with item parser
page = Page.from_dict(response_data, Coin.from_dict)

# Use like a list
print(f"Page has {len(page)} items")
for coin in page:
    print(f"Coin: {coin.coin_type}")

# Pagination info
if page.has_next_page:
    print(f"Next cursor: {page.next_cursor}")
```

## Updated Coin Query API

The `CoinQueryClient` now returns typed objects instead of raw dictionaries:

```python
from sui_py import SuiClient, SuiAddress

async with SuiClient("https://fullnode.mainnet.sui.io:443") as client:
    address = SuiAddress.from_str("0x...")
    
    # Returns List[Balance] instead of List[Dict]
    balances = await client.coin_query.get_all_balances(address)
    
    # Returns Page[Coin] instead of Dict
    coins = await client.coin_query.get_all_coins(address, limit=10)
    
    # Returns SuiCoinMetadata instead of Dict
    metadata = await client.coin_query.get_coin_metadata("0x2::sui::SUI")
    
    # Type-safe operations
    for balance in balances:
        if not balance.is_zero():
            print(f"{balance.coin_type}: {balance.total_balance}")
    
    # Pagination
    for coin in coins:
        formatted_balance = metadata.format_amount(coin.balance_int)
        print(f"Coin {coin.coin_object_id}: {formatted_balance} SUI")
```

## Benefits

1. **Type Safety**: Catch errors at development time with proper type hints
2. **Validation**: Automatic validation of addresses, object IDs, and other formats
3. **IDE Support**: Full autocomplete and IntelliSense support
4. **Error Messages**: Clear, descriptive error messages for validation failures
5. **Convenience**: Helper methods like `is_zero()`, `format_amount()`, etc.
6. **Consistency**: Uniform interface across all API responses
7. **Future-Proof**: Easy to extend with additional validation and methods

## Testing

Comprehensive tests are included in `tests/test_coin_schemas.py` covering:

- Base type validation and edge cases
- Coin type creation and methods
- Pagination functionality
- Round-trip serialization
- Error handling

Run tests with:
```bash
python -m pytest tests/test_coin_schemas.py -v
```

## Examples

See `examples/typed_coin_query_example.py` for a complete demonstration of the typed API in action, including:

- Type-safe coin queries
- Pagination handling
- Amount formatting
- Error handling
- Type validation demonstrations 