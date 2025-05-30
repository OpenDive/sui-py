# sui-py
SuiPy – a deliciously lightweight, high-performance Python SDK for the Sui blockchain

## Design Philosophy

- **Async-First**: Built for high-performance concurrent operations
- **Type-Safe**: Full type hints and structured data models
- **Lightweight**: Minimal dependencies, maximum performance

## Current Status

✅ **Extended API Complete** - All RPC methods implemented with full type safety

✅ **Cryptographic Primitives** - Ed25519 signing, verification, and key management

✅ **BCS Serialization** - Complete Binary Canonical Serialization implementation

✅ **Transaction Building** - Complete Programmable Transaction Block (PTB) system

🚧 **In Development** - Write APIs for transaction execution

### Async-First Design

This SDK is designed with async/await as the primary interface for optimal performance with I/O-bound blockchain operations. A synchronous wrapper may be added in the future based on user demand.

```python
# Async interface (current)
async with SuiClient("mainnet") as client:
    balance = await client.coin_query.get_balance(address)
    coins = await client.coin_query.get_all_coins(address)
    objects = await client.extended_api.get_owned_objects(address)
```

## Features

### ✅ Implemented

- **Transaction Building System**: Complete Programmable Transaction Block (PTB) implementation
  - **TransactionBuilder**: Fluent API for building complex transactions
  - **Type-Safe Arguments**: PureArgument, ObjectArgument, ResultArgument with automatic conversion
  - **Full Command Support**: Move calls, object transfers, coin operations, package management
  - **Result Chaining**: Use outputs from one command as inputs to another
  - **BCS Integration**: Complete serialization/deserialization with the existing BCS system
  - **Input Deduplication**: Automatic optimization of duplicate inputs
  - **Validation**: Comprehensive validation including forward reference detection
  - **Error Handling**: Descriptive error messages for debugging

- **BCS (Binary Canonical Serialization)**: Complete implementation following Move language specification
  - **Protocol-based Architecture**: Type-safe `Serializable`/`Deserializable` protocols
  - **Full Move Type Support**: All primitive types (U8, U16, U32, U64, U128, U256, Bool, Bytes, FixedBytes)
  - **Generic Containers**: `BcsVector<T>` and `BcsOption<T>` for any serializable type
  - **Deterministic Output**: Exact BCS format compliance with little-endian encoding
  - **ULEB128 Support**: Variable-length integer encoding for collections
  - **Comprehensive Error Handling**: Hierarchical exception system with detailed context
  - **Factory Functions**: Convenient constructors (`u8()`, `u16()`, etc.)

- **Cryptographic Primitives**: Complete Ed25519 implementation with unified signature handling
  - `create_private_key()` - Generate new Ed25519 private keys
  - `import_private_key()` - Import keys from bytes or hex
  - **Ed25519PrivateKey**: Key generation, signing, serialization
  - **Ed25519PublicKey**: Signature verification, Sui address derivation
  - **Signature**: Unified signature class for all cryptographic schemes
  - **SignatureScheme**: Support for Ed25519 (Secp256k1 and Secp256r1 coming soon)
  - Sui address derivation with proper BLAKE2b hashing and scheme flags

- **Coin Query API**: Complete implementation of all coin-related RPC methods
  - `get_all_balances()` - Get all coin balances for an address
  - `get_all_coins()` - Get all coin objects (with pagination)
  - `get_balance()` - Get balance for specific coin type
  - `get_coin_metadata()` - Get coin metadata
  - `get_coins()` - Get coins of specific type (with pagination)
  - `get_total_supply()` - Get total supply of a coin type

- **Extended API**: Complete implementation of extended RPC methods
  - `get_dynamic_fields()` - Get dynamic field info for an object
  - `get_dynamic_field_object()` - Get dynamic field object data
  - `get_owned_objects()` - Get objects owned by an address (with pagination)
  - `query_events()` - Query events with filters (with pagination)
  - `query_transaction_blocks()` - Query transaction blocks (with pagination)
  - `resolve_name_service_address()` - Resolve name to address
  - `resolve_name_service_names()` - Get names for an address
  - Note: Subscription methods require WebSocket support (not implemented in REST client)

- **Event Indexer Example**: Production-ready blockchain event processing
  - Real-time event monitoring with typed `SuiEvent` objects
  - Automatic cursor tracking and database persistence
  - Modular handler architecture for different event types
  - Auto-setup with Prisma Client Python integration
  - Exponential backoff retry logic and error handling

### 🚧 Coming Soon
- Secp256k1 and Secp256r1 cryptographic schemes
- Account abstraction with multi-scheme support
- Mnemonic phrase support for key derivation
- Read API (checkpoints, protocol config)
- Write API (transaction execution)
- Governance Read API
- Move Utils API
- WebSocket client for subscriptions

## Installation

### From PyPI (Coming Soon)
```bash
pip install sui-py
```

### Development Setup

#### Option 1: Automated Setup (Recommended)

**Using Python script** (cross-platform):
```bash
git clone https://github.com/your-org/sui-py
cd sui-py
python scripts/setup_dev.py
```

**Using Bash script** (macOS/Linux):
```bash
git clone https://github.com/your-org/sui-py
cd sui-py
./scripts/setup_dev.sh
```

#### Option 2: Manual Setup

1. **Clone the repository**:
```bash
git clone https://github.com/your-org/sui-py
cd sui-py
```

2. **Create and activate a virtual environment**:

**Using venv (recommended)**:
```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

**Using conda**:
```bash
# Create virtual environment
conda create -n sui-py python=3.8+
conda activate sui-py
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Install in development mode** (optional):
```bash
pip install -e .
```

5. **Install development tools** (optional):
```bash
pip install -r requirements-dev.txt
```

## Quick Start

### BCS Serialization
```python
from sui_py.bcs import (
    serialize, deserialize, U64, U8, Bool, Bytes,
    BcsVector, BcsOption, bcs_vector, bcs_some, bcs_none
)

# Serialize primitive types
value = U64(12345)
data = serialize(value)
print(f"Serialized: {data.hex()}")

# Deserialize back
restored = deserialize(data, U64.deserialize)
print(f"Value: {restored.value}")

# Work with containers
vector = bcs_vector([U8(1), U8(2), U8(3)])
vector_data = serialize(vector)

# Options (nullable types)
some_value = bcs_some(U64(999))
none_value = bcs_none()

# Factory functions for convenience
from sui_py.bcs import u8, u64, boolean, bytes_value

small_num = u8(255)
big_num = u64(1_000_000)
flag = boolean(True)
data = bytes_value(b"hello world")
```

### Cryptographic Operations
```python
from sui_py import SignatureScheme, create_private_key, Ed25519PrivateKey, Signature

# Generate a new Ed25519 key pair
private_key = create_private_key(SignatureScheme.ED25519)
public_key = private_key.public_key()

# Get the Sui address
address = public_key.to_sui_address()
print(f"Address: {address}")

# Sign a message
message = b"Hello, Sui blockchain!"
signature = private_key.sign(message)

# Verify the signature
is_valid = public_key.verify(message, signature)
print(f"Signature valid: {is_valid}")

# Export/import keys
private_key_hex = private_key.to_hex()
imported_key = Ed25519PrivateKey.from_hex(private_key_hex)

# Serialize signatures
signature_hex = signature.to_hex()
reconstructed_sig = Signature.from_hex(signature_hex, SignatureScheme.ED25519)
```

### Transaction Building
```python
from sui_py import TransactionBuilder, ProgrammableTransactionBlock

# Build a simple coin transfer transaction
tx = TransactionBuilder()

# Add inputs
coin = tx.object("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
amount = tx.pure(1000, "u64")
recipient = tx.pure("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")

# Split coins and transfer
new_coins = tx.split_coins(coin, [amount])
tx.transfer_objects([new_coins[0]], recipient)

# Build the transaction
ptb = tx.build()
print(f"Transaction summary: {ptb}")

# Get bytes for signing
tx_bytes = tx.to_bytes()

# Complex DeFi operations with result chaining
defi_tx = TransactionBuilder()

# Get gas coin and split for operations
gas = defi_tx.gas_coin()
operation_coins = defi_tx.split_coins(gas, [1000, 2000])

# Call a Move function with the split coins
pool = defi_tx.object("0x...")
liquidity_result = defi_tx.move_call(
    "0x123::pool::add_liquidity",
    arguments=[pool, operation_coins[0]],
    type_arguments=["0x2::sui::SUI", "0x456::token::USDC"]
)

# Use the result in another operation
lp_tokens = liquidity_result.single()
defi_tx.transfer_objects([lp_tokens], recipient)

# Serialize the complex transaction
complex_ptb = defi_tx.build()
complex_bytes = defi_tx.to_bytes()
```

### Coin Query API
```python
import asyncio
from sui_py import SuiClient

async def main():
    # Connect to mainnet
    async with SuiClient("mainnet") as client:
        # Get all balances for an address
        balances = await client.coin_query.get_all_balances(
            "0x94f1a597b4e8f709a396f7f6b1482bdcd65a673d111e49286c527fab7c2d0961"
        )
        
        for balance in balances:
            print(f"{balance['coinType']}: {balance['totalBalance']}")

asyncio.run(main())
```

### Extended API
```python
import asyncio
from sui_py import SuiClient

async def main():
    async with SuiClient("testnet") as client:
        # Get owned objects
        objects = await client.extended_api.get_owned_objects(
            owner="0x...",
            limit=10
        )
        
        # Query events
        events = await client.extended_api.query_events(
            query={"All": []},
            limit=5
        )
        
        # Query transactions
        transactions = await client.extended_api.query_transaction_blocks(
            query={"FromAddress": "0x..."},
            limit=5
        )

asyncio.run(main())
```

## Testing

### Running Tests

The project includes comprehensive test suites for all implemented features.

#### Prerequisites
Make sure you have the development environment set up:

```bash
# Install dependencies including test tools
pip install -r requirements.txt
pip install -r requirements-dev.txt  # if available
```

#### Run All Tests
```bash
# Run all tests with pytest
python -m pytest

# Run with verbose output
python -m pytest -v

# Run with coverage report
python -m pytest --cov=sui_py
```

#### Run Specific Test Suites

**BCS Tests** (Binary Canonical Serialization):
```bash
# Run BCS tests specifically
python -m pytest tests/test_bcs.py -v

# Run individual test classes
python -m pytest tests/test_bcs.py::TestPrimitiveTypes -v
python -m pytest tests/test_bcs.py::TestContainerTypes -v
python -m pytest tests/test_bcs.py::TestErrorHandling -v

# Run the basic smoke test
cd tests
python test_bcs.py
```

**Cryptographic Tests**:
```bash
# Run crypto tests (if available)
python -m pytest tests/test_crypto.py -v
```

**API Tests**:
```bash
# Run API tests (if available)
python -m pytest tests/test_api.py -v
```

#### Test Coverage

The test suite covers:

- **Transaction Building System**:
  - ✅ Basic transaction construction (coin splits, transfers, Move calls)
  - ✅ Complex result chaining and argument handling
  - ✅ Package publishing and upgrading operations
  - ✅ BCS serialization round-trip testing
  - ✅ Input validation and error handling
  - ✅ PTB validation and dependency checking

- **BCS Implementation** (37 test cases - enhanced from C# Sui Unity SDK):
  - ✅ **Comprehensive Primitive Types**: All integer types (U8, U16, U32, U64, U128, U256) with exact value testing
  - ✅ **Boolean Operations**: Separate true/false serialization and invalid data error handling
  - ✅ **String & Byte Handling**: UTF-8 string serialization, byte arrays, and fixed-length bytes
  - ✅ **BigInteger Support**: Large number handling for U128/U256 with values from C# test cases
  - ✅ **ULEB128 Encoding**: Direct low-level testing of variable-length integer encoding
  - ✅ **Container Types**: BcsVector, BcsOption with nested containers and string sequences
  - ✅ **Complex Serialization**: Multi-level nested structures simulating transaction patterns
  - ✅ **Error Handling**: Overflow detection, insufficient data, invalid formats, malformed booleans
  - ✅ **Round-trip Validation**: Complete serialization/deserialization cycle testing
  - ✅ **Factory Functions**: Convenience APIs and type-safe constructors

- **Cryptographic Primitives**:
  - ✅ Ed25519 key generation, signing, and verification
  - ✅ Sui address derivation
  - ✅ Signature serialization/deserialization

#### Continuous Integration
```bash
# Run the same checks as CI
python -m pytest --cov=sui_py --cov-report=term-missing
python -m flake8 sui_py tests  # if configured
python -m mypy sui_py  # if configured
```

## Supported Networks

- `mainnet` - Sui Mainnet
- `testnet` - Sui Testnet  
- `devnet` - Sui Devnet
- `localnet` - Local Sui node (http://127.0.0.1:9000)
- Custom RPC endpoints

## Error Handling

```python
from sui_py import SuiClient, SuiError, SuiRPCError, SuiValidationError
from sui_py import TransactionBuilder
from sui_py.bcs import BcsError, SerializationError, DeserializationError

# API Error Handling
async with SuiClient("mainnet") as client:
    try:
        balance = await client.coin_query.get_balance("invalid-address")
    except SuiValidationError as e:
        print(f"Invalid input: {e}")
    except SuiRPCError as e:
        print(f"RPC error {e.code}: {e}")
    except SuiError as e:
        print(f"General Sui error: {e}")

# Transaction Building Error Handling
try:
    tx = TransactionBuilder()
    tx.move_call("invalid_target")  # Invalid format
except ValueError as e:
    print(f"Invalid Move call: {e}")

try:
    tx = TransactionBuilder()
    tx.object("invalid_object_id")  # Invalid object ID
except ValueError as e:
    print(f"Invalid object ID: {e}")

try:
    tx = TransactionBuilder()
    ptb = tx.build()  # Empty transaction
except ValueError as e:
    print(f"Transaction validation failed: {e}")

# BCS Error Handling
try:
    data = serialize(U8(256))  # Overflow error
except OverflowError as e:
    print(f"Value too large: {e}")

try:
    result = deserialize(b'\x01', U32.deserialize)  # Insufficient data
except DeserializationError as e:
    print(f"Deserialization failed: {e}")
```

## Examples

### Real-World Event Indexer

Check out our complete **Event Indexer** implementation in `examples/event_indexer/`:

```python
# Real-time blockchain event processing with cursor tracking
from sui_py import SuiClient, EventFilter

async with SuiClient("testnet") as client:
    events = await client.extended_api.query_events(
        query=EventFilter.by_module(package_id, "lock"),
        limit=50
    )
    # Process events with typed handlers...
```

**Features:**
- ✅ Real-time event processing with typed `SuiEvent` objects
- ✅ Automatic cursor tracking and database persistence  
- ✅ Production-ready error handling and retry logic
- ✅ Auto-setup with Prisma Client Python
- ✅ Feature parity with TypeScript reference implementation

### Quick Examples

See the `examples/` directory for complete usage examples:
- `transaction_building_example.py` - Comprehensive transaction building with PTBs, result chaining, and BCS serialization
- `coin_query_example.py` - Comprehensive Coin Query API usage
- `extended_api_example.py` - Extended API usage with objects, events, and transactions
- `crypto_example.py` - Cryptographic operations and key management
- `bcs_example.py` - BCS serialization and deserialization examples

## Contributing

This project is in active development. Contributions are welcome!

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite: `python -m pytest`
5. Submit a pull request

## License

MIT License
