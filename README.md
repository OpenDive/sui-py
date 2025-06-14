<div align="center">
  <img src="public/assets/SuiPy-banner.png" alt="SuiPy Banner" />
</div>

# sui-py
SuiPy – a deliciously lightweight, high-performance Python SDK for the Sui blockchain

## Table of Contents

- [Design Philosophy](#design-philosophy)
- [Current Status](#current-status)
- [Features](#features)
  - [Async-First Design](#async-first-design)
  - [✅ Implemented](#-implemented)
  - [🚧 Coming Soon](#-coming-soon)
- [Installation](#installation)
  - [From PyPI (Coming Soon)](#from-pypi-coming-soon)
  - [From Git Repository](#from-git-repository)
  - [Development Setup](#development-setup)
- [Quick Start](#quick-start)
  - [BCS Serialization](#bcs-serialization)
  - [Account Management](#account-management)
  - [HD Wallet Operations](#hd-wallet-operations)
  - [Cryptographic Operations](#cryptographic-operations)
  - [Transaction Building](#transaction-building)
  - [Coin Query API](#coin-query-api)
  - [Governance Read API](#governance-read-api)
  - [Extended API](#extended-api)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Test Coverage](#test-coverage)
- [Supported Networks](#supported-networks)
- [Error Handling](#error-handling)
- [Examples](#examples)
  - [Real-World Event Indexer](#real-world-event-indexer)
  - [Quick Examples](#quick-examples)
- [Contributing](#contributing)
- [License](#license)

## Design Philosophy

- **Async-First**: Built for high-performance concurrent operations
- **Type-Safe**: Full type hints and structured data models
- **Lightweight**: Minimal dependencies, maximum performance

## Current Status

✅ **Extended API Complete** - All RPC methods implemented with full type safety

✅ **Cryptographic Primitives** - Ed25519 signing, verification, and key management

✅ **BCS Serialization** - Complete Binary Canonical Serialization implementation

✅ **Transaction Building & Serialization** - **VERIFIED C# Unity SDK Compatibility** - Complete Programmable Transaction Block (PTB) system with byte-for-byte serialization matching

✅ **Low-Level Transaction Compatibility** - Direct transaction construction and serialization works without RPC requirements

✅ **Governance Read API** - Complete validator and staking information queries

✅ **TransactionBuilder APIs** - Complete high-level transaction building with result chaining, argument validation, and BCS serialization (RPC-optional for basic operations)

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

- **Transaction Building & Serialization System**: Complete Programmable Transaction Block (PTB) implementation with **VERIFIED C# Unity SDK byte-for-byte compatibility**
  - **Low-Level Direct Construction** ✅: Direct object creation and serialization (no RPC required)
    - Manual PTB, Command, and TransactionData construction
    - Complete BCS serialization with exact C# Unity SDK byte matching
    - ObjectArgument, InputArgument, ResultArgument with proper variant encoding
    - MoveCall with correct package/module/function format
    - TransactionExpiration, GasData, and full transaction structure support
  - **High-Level TransactionBuilder** ✅: Fluent API for building transactions with comprehensive functionality
    - Complete transaction building with object/pure argument creation (no RPC required)
    - Result chaining between commands with automatic input deduplication
    - Move call support with proper package/module/function resolution
    - Coin operations: split, merge, transfer with type safety
    - Object operations: transfer, publish, upgrade with validation
    - Advanced features requiring RPC: gas estimation, object resolution from network state
  - **Type-Safe Arguments**: PureArgument, ObjectArgument, ResultArgument, InputArgument with automatic conversion
  - **Full Command Support**: Move calls, object transfers, coin operations, package management
  - **Result Chaining**: Use outputs from one command as inputs to another
  - **BCS Integration**: Complete serialization/deserialization with exact C# Unity SDK byte compatibility
  - **Input Deduplication**: Automatic optimization of duplicate inputs
  - **Validation**: Comprehensive validation including forward reference detection
  - **Error Handling**: Descriptive error messages for debugging
  - **Cross-Language Compatibility**: Verified byte-for-byte serialization matching with C# Unity SDK test cases

- **BCS (Binary Canonical Serialization)**: Complete implementation following Move language specification
  - **Protocol-based Architecture**: Type-safe `Serializable`/`Deserializable` protocols
  - **Full Move Type Support**: All primitive types (U8, U16, U32, U64, U128, U256, Bool, Bytes, FixedBytes)
  - **Generic Containers**: `BcsVector<T>` and `BcsOption<T>` for any serializable type
  - **Deterministic Output**: Exact BCS format compliance with little-endian encoding
  - **ULEB128 Support**: Variable-length integer encoding for collections
  - **Comprehensive Error Handling**: Hierarchical exception system with detailed context
  - **Factory Functions**: Convenient constructors (`u8()`, `u16()`, etc.)

- **Account Abstraction**: Complete account management with multi-scheme support
  - **Account**: Single key pair accounts supporting all Sui signature schemes
  - **AbstractAccount**: Base interface for polymorphic account usage
  - Seamless integration with existing cryptographic primitives
  - Account serialization and restoration for secure storage
  - Multiple creation methods: generate, import from hex/bytes/base64
  - Full signing and verification capabilities with automatic address derivation

- **HD Wallet**: BIP32/BIP39 hierarchical deterministic wallet functionality
  - **HDWallet**: Complete HD wallet implementation following industry standards
  - **DerivationPath**: BIP32 derivation path utilities and validation
  - **SuiDerivationPath**: Sui-specific derivation path standards (m/44'/784'/0'/0'/index')
  - Mnemonic generation and validation (12, 15, 18, 21, 24 words)
  - Multi-scheme account derivation (Ed25519, Secp256k1 from same seed)
  - Deterministic account recovery from mnemonic phrases
  - Account caching and management with wallet serialization
  - Standard BIP39/BIP32 compliance for cross-platform compatibility

- **Cryptographic Primitives**: Complete Ed25519 and Secp256k1 implementation with unified signature handling
  - `create_private_key()` - Generate new Ed25519 and Secp256k1 private keys
  - `import_private_key()` - Import keys from bytes or hex
  - **Ed25519PrivateKey**: Key generation, signing, serialization
  - **Ed25519PublicKey**: Signature verification, Sui address derivation
  - **Secp256k1PrivateKey**: Key generation, signing, serialization
  - **Secp256k1PublicKey**: Signature verification, Sui address derivation
  - **Signature**: Unified signature class for all cryptographic schemes
  - **SignatureScheme**: Support for Ed25519 and Secp256k1 (Secp256r1 coming soon)
  - Sui address derivation with proper BLAKE2b hashing and scheme flags

- **Governance Read API**: Complete implementation of governance-related RPC methods
  - `get_committee_info()` - Get committee information for specific epoch
  - `get_latest_sui_system_state()` - Get comprehensive system state information
  - `get_reference_gas_price()` - Get current network reference gas price
  - `get_stakes()` - Get all delegated stakes owned by an address
  - `get_stakes_by_ids()` - Get delegated stakes by specific staked SUI IDs
  - `get_validators_apy()` - Get validator APY information for current epoch

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
- Secp256r1 cryptographic scheme
- Read API (checkpoints, protocol config)
- Write API (transaction execution)
- Move Utils API
- WebSocket client for subscriptions

## Installation

### From PyPI (Coming Soon)
```bash
pip install sui-py
```

### From Git Repository

You can install the latest version directly from the git repository:

```bash
# Install latest from main branch
pip install git+https://github.com/OpenDive/sui-py.git

# Install specific version/tag
pip install git+https://github.com/OpenDive/sui-py.git@v0.1.0

# Install specific branch  
pip install git+https://github.com/OpenDive/sui-py.git@feature-branch

# Install with development dependencies
pip install "git+https://github.com/OpenDive/sui-py.git[dev]"
```

### Development Setup

#### Option 1: Automated Setup (Recommended)

**Using Python script** (cross-platform):
```bash
git clone https://github.com/OpenDive/sui-py
cd sui-py
python scripts/setup_dev.py
```

**Using Bash script** (macOS/Linux):
```bash
git clone https://github.com/OpenDive/sui-py
cd sui-py
./scripts/setup_dev.sh
```

#### Option 2: Manual Setup

1. **Clone the repository**:
```bash
git clone https://github.com/OpenDive/sui-py
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

### Account Management
```python
from sui_py import Account, SignatureScheme

# Generate accounts for different signature schemes
ed25519_account = Account.generate(SignatureScheme.ED25519)
secp256k1_account = Account.generate(SignatureScheme.SECP256K1)

print(f"Ed25519 Address: {ed25519_account.address}")
print(f"Secp256k1 Address: {secp256k1_account.address}")

# Sign and verify messages
message = b"Hello, Sui blockchain!"
signature = ed25519_account.sign(message)
is_valid = ed25519_account.verify(message, signature)
print(f"Signature valid: {is_valid}")

# Serialize account for secure storage
account_data = ed25519_account.to_base64()
print(f"Serialized account: {account_data}")

# Restore account from serialized data
restored_account = Account.from_base64(account_data)
print(f"Restored address: {restored_account.address}")

# Import account from existing private key
private_key_hex = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12"
imported_account = Account.from_hex(private_key_hex, SignatureScheme.ED25519)
```

### HD Wallet Operations
```python
from sui_py import HDWallet, SignatureScheme, SuiDerivationPath

# Generate a new HD wallet with mnemonic
wallet = HDWallet.generate()
print(f"Mnemonic: {wallet.mnemonic}")

# Or restore from existing mnemonic
mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
wallet = HDWallet.from_mnemonic(mnemonic)

# Derive accounts for different signature schemes
ed25519_account = wallet.derive_account(0, SignatureScheme.ED25519)
secp256k1_account = wallet.derive_account(0, SignatureScheme.SECP256K1)

print(f"Ed25519 Account 0: {ed25519_account.address}")
print(f"Secp256k1 Account 0: {secp256k1_account.address}")

# Both accounts derived from the same index will be deterministic
# Re-deriving the same account returns identical results
same_account = wallet.derive_account(0, SignatureScheme.ED25519)
assert ed25519_account.address == same_account.address

# Get multiple accounts at once
accounts = wallet.get_accounts(SignatureScheme.ED25519, count=5)
for i, account in enumerate(accounts):
    print(f"Account {i}: {account.address}")

# Work with custom derivation paths
custom_path = SuiDerivationPath.account_path(2)  # m/44'/784'/0'/0'/2'
custom_account = wallet.derive_account_from_path(custom_path, SignatureScheme.ED25519)

# Serialize wallet for secure storage (without mnemonic for security)
wallet_data = wallet.to_dict()
# Note: This excludes the mnemonic for security - store it separately!
```

### Cryptographic Operations
```python
from sui_py import SignatureScheme, create_private_key, Ed25519PrivateKey, Secp256k1PrivateKey, Signature

# Generate Ed25519 key pair
ed25519_private_key = create_private_key(SignatureScheme.ED25519)
ed25519_public_key = ed25519_private_key.public_key()

# Generate Secp256k1 key pair
secp256k1_private_key = create_private_key(SignatureScheme.SECP256K1)
secp256k1_public_key = secp256k1_private_key.public_key()

# Get Sui addresses for both schemes
ed25519_address = ed25519_public_key.to_sui_address()
secp256k1_address = secp256k1_public_key.to_sui_address()
print(f"Ed25519 Address: {ed25519_address}")
print(f"Secp256k1 Address: {secp256k1_address}")

# Sign a message with both schemes
message = b"Hello, Sui blockchain!"

ed25519_signature = ed25519_private_key.sign(message)
secp256k1_signature = secp256k1_private_key.sign(message)

# Verify signatures
ed25519_valid = ed25519_public_key.verify(message, ed25519_signature)
secp256k1_valid = secp256k1_public_key.verify(message, secp256k1_signature)
print(f"Ed25519 signature valid: {ed25519_valid}")
print(f"Secp256k1 signature valid: {secp256k1_valid}")

# Export/import keys for both schemes
ed25519_hex = ed25519_private_key.to_hex()
secp256k1_hex = secp256k1_private_key.to_hex()

imported_ed25519 = Ed25519PrivateKey.from_hex(ed25519_hex)
imported_secp256k1 = Secp256k1PrivateKey.from_hex(secp256k1_hex)

# Serialize signatures with scheme information
ed25519_sig_hex = ed25519_signature.to_hex()
secp256k1_sig_hex = secp256k1_signature.to_hex()

reconstructed_ed25519 = Signature.from_hex(ed25519_sig_hex, SignatureScheme.ED25519)
reconstructed_secp256k1 = Signature.from_hex(secp256k1_sig_hex, SignatureScheme.SECP256K1)
```

### Transaction Building

**Low-Level Direct Construction** (No RPC Required):
```python
from sui_py.transactions import (
    TransactionData, TransactionDataV1, TransactionType,
    TransactionKind, TransactionKindType, GasData, TransactionExpiration,
    ProgrammableTransactionBlock, Command, MoveCall,
    ObjectArgument, InputArgument, ResultArgument
)
from sui_py.types import ObjectRef, SuiAddress
from sui_py.bcs import serialize

# Create transaction data directly (equivalent to C# Unity SDK)
object_ref = ObjectRef(
    object_id="0x1000000000000000000000000000000000000000000000000000000000000000",
    version=10000,
    digest="1Bhh3pU9gLXZhoVxkr5wyg9sX6"
)

# Build PTB directly
object_arg = ObjectArgument(object_ref)
move_call = MoveCall(
    package="0x0000000000000000000000000000000000000000000000000000000000000002",
    module="display",
    function="new",
    type_arguments=["0x0000000000000000000000000000000000000000000000000000000000000002::capy::Capy"],
    arguments=[InputArgument(0)]
)

ptb = ProgrammableTransactionBlock(
    inputs=[object_arg],
    commands=[Command(move_call)]
)

# Create complete transaction
transaction_kind = TransactionKind(
    kind_type=TransactionKindType.ProgrammableTransaction,
    programmable_transaction=ptb
)

gas_data = GasData(
    budget="1000000",
    price="1",
    payment=[object_ref],
    owner=SuiAddress.from_hex("0x0000000000000000000000000000000000000000000000000000000000000002")
)

transaction_data = TransactionData(
    transaction_type=TransactionType.V1,
    transaction_data_v1=TransactionDataV1(
        transaction_kind=transaction_kind,
        sender=SuiAddress.from_hex("0x0000000000000000000000000000000000000000000000000000000000000BAD"),
        gas_data=gas_data,
        expiration=TransactionExpiration()
    )
)

# Serialize for signing (byte-for-byte compatible with C# Unity SDK)
tx_bytes = serialize(transaction_data)
```

**High-Level TransactionBuilder** (Some features require RPC):
```python
from sui_py import TransactionBuilder, ProgrammableTransactionBlock

# Build a simple coin transfer transaction
tx = TransactionBuilder()

# Add inputs (basic functionality works without RPC)
coin = tx.object("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
amount = tx.pure(1000, "u64")
recipient = tx.pure("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")

# Split coins and transfer
new_coins = tx.split_coins(coin, [amount])
tx.transfer_objects([new_coins[0]], recipient)

# Build the transaction
ptb = tx.build()
print(f"Transaction has {len(ptb.commands)} commands")
print(f"Transaction has {len(ptb.inputs)} inputs")

# Get bytes for signing
tx_bytes = tx.to_bytes()
print(f"Transaction bytes length: {len(tx_bytes)}")

# Complex DeFi operations with result chaining (works without RPC)
defi_tx = TransactionBuilder()

# Create a complex transaction with multiple operations
pool = defi_tx.object("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
token_amount = defi_tx.pure(1000000, "u64")

# Add liquidity to a pool
liquidity_result = defi_tx.move_call(
    "0x123::pool::add_liquidity",
    arguments=[pool, token_amount],
    type_arguments=["0x2::sui::SUI", "0x456::token::USDC"]
)

# Use the result in another operation - result chaining works perfectly
lp_tokens = liquidity_result.result(0)  # First return value
defi_tx.transfer_objects([lp_tokens], recipient)

# Split coins and use results
coin_splits = defi_tx.split_coins(coin, [tx.pure(500, "u64"), tx.pure(300, "u64")])
defi_tx.transfer_objects([coin_splits.result(0)], recipient)
defi_tx.transfer_objects([coin_splits.result(1)], recipient)

# Build and serialize - everything works without RPC
complex_ptb = defi_tx.build()
complex_bytes = defi_tx.to_bytes()
print(f"Complex transaction: {len(complex_ptb.commands)} commands, {len(complex_bytes)} bytes")
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

### Governance Read API
```python
import asyncio
from sui_py import SuiClient

async def main():
    async with SuiClient("mainnet") as client:
        # Get current system state
        system_state = await client.governance_read.get_latest_sui_system_state()
        print(f"Current epoch: {system_state.epoch}")
        print(f"Total stake: {system_state.total_stake}")
        print(f"Active validators: {len(system_state.active_validators)}")
        
        # Get validator APYs
        validator_apys = await client.governance_read.get_validators_apy()
        for validator_apy in validator_apys.apys[:5]:  # Show top 5
            print(f"Validator {validator_apy.address}: {validator_apy.apy:.2%} APY")
        
        # Get stakes for an address
        stakes = await client.governance_read.get_stakes("0x...")
        for stake in stakes:
            print(f"Staked with validator {stake.validator_address}")

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

**Low-Level Transaction Serialization Tests** (C# Unity SDK Compatibility):
```bash
# Direct transaction construction and serialization (no RPC required)
python -m pytest tests/test_transactions_serialization.py -v

# Test C# Unity SDK byte-for-byte compatibility
python -m pytest tests/test_transactions_serialization.py::TestTransactionsSerialization::test_transaction_data_serialization_single_input -v
python -m pytest tests/test_transactions_serialization.py::TestTransactionsSerialization::test_transaction_data_serialization_multiple_args -v
```

**High-Level TransactionBuilder Tests**:
```bash
# TransactionBuilder tests - comprehensive coverage of builder functionality
python -m pytest tests/test_transactions.py -v

# Test specific builder functionality:
python -m pytest tests/test_transactions.py::TestTransactionBuilder::test_basic_transaction_building -v
python -m pytest tests/test_transactions.py::TestTransactionBuilder::test_result_chaining -v
python -m pytest tests/test_transactions.py::TestTransactionBuilder::test_move_call_operations -v
```

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

- **Transaction Building & Serialization System**:
  - ✅ **VERIFIED C# Unity SDK Compatibility**: Byte-for-byte serialization matching with official C# test cases in `tests/test_transactions_serialization.py`
  - ✅ **Low-Level Direct Construction**: Manual PTB, Command, and TransactionData creation without RPC requirements
  - ✅ **Argument Type System**: ObjectArgument (variant 0 - ImmOrOwned), InputArgument, ResultArgument validation
  - ✅ **Complex Transaction Patterns**: Multi-input/multi-command transaction structures
  - ✅ **Result Chaining**: Command outputs used as inputs in subsequent commands  
  - ✅ **PTB Structure Validation**: Input deduplication and command dependency checking
  - ✅ **BCS Round-trip Testing**: Complete serialization/deserialization verification
  - ✅ **Cross-Language Verification**: Python serialization exactly matches C# Unity SDK output (304 & 310 bytes)
  - ✅ **Error Handling**: Input validation and transaction building error cases
  - ✅ **High-Level TransactionBuilder**: Complete test coverage including result chaining, argument validation, and complex transaction patterns

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

# Account and HD Wallet Error Handling
from sui_py import Account, HDWallet, InvalidDerivationPathError, WalletError

try:
    # Invalid private key format
    account = Account.from_hex("invalid_key", SignatureScheme.ED25519)
except ValueError as e:
    print(f"Invalid private key: {e}")

try:
    # Invalid mnemonic phrase
    wallet = HDWallet.from_mnemonic("invalid mnemonic phrase")
except ValueError as e:
    print(f"Invalid mnemonic: {e}")

try:
    # Invalid derivation path
    from sui_py.wallets.derivation import DerivationPath
    path = DerivationPath.from_string("invalid/path")
except InvalidDerivationPathError as e:
    print(f"Invalid derivation path: {e}")

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
- `account_usage.py` - Complete Account abstraction examples with multi-scheme support *(no RPC required)*
- `hd_wallet_usage.py` - HD Wallet operations including mnemonic generation, account derivation, and management *(no RPC required)*
- `transaction_building_example.py` - Comprehensive transaction building with PTBs, result chaining, and BCS serialization
- `coin_query_example.py` - Comprehensive Coin Query API usage *(requires RPC)*
- `extended_api_example.py` - Extended API usage with objects, events, and transactions *(requires RPC)*
- `crypto_example.py` - Cryptographic operations and key management *(no RPC required)*
- `bcs_example.py` - BCS serialization and deserialization examples *(no RPC required)*

**Note**: Examples marked with *(requires RPC)* need a live Sui network connection. Examples marked with *(no RPC required)* work offline with hardcoded values.

For **low-level transaction construction** examples that work without RPC, see the test file:
- `tests/test_transactions_serialization.py` - Direct transaction construction with C# Unity SDK compatibility

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