# sui-py
SuiPy – a deliciously lightweight, high-performance Python SDK for the Sui blockchain

## Design Philosophy

- **Async-First**: Built for high-performance concurrent operations
- **Type-Safe**: Full type hints and structured data models (coming soon)
- **Lightweight**: Minimal dependencies, maximum performance

## Current Status

✅ **Extended API Complete** - All RPC methods implemented with full type safety

🚧 **In Development** - Transaction Builder and Write APIs

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
- Read API (checkpoints, protocol config)
- Transaction Builder API
- Write API (transaction execution)
- Governance Read API
- Move Utils API
- Typed data models (Address, ObjectID, etc.)
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

## Supported Networks

- `mainnet` - Sui Mainnet
- `testnet` - Sui Testnet  
- `devnet` - Sui Devnet
- `localnet` - Local Sui node (http://127.0.0.1:9000)
- Custom RPC endpoints

## Error Handling

```python
from sui_py import SuiClient, SuiError, SuiRPCError, SuiValidationError

async with SuiClient("mainnet") as client:
    try:
        balance = await client.coin_query.get_balance("invalid-address")
    except SuiValidationError as e:
        print(f"Invalid input: {e}")
    except SuiRPCError as e:
        print(f"RPC error {e.code}: {e}")
    except SuiError as e:
        print(f"General Sui error: {e}")
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
- `coin_query_example.py` - Comprehensive Coin Query API usage
- `extended_api_example.py` - Extended API usage with objects, events, and transactions

## Contributing

This project is in active development. Contributions are welcome!

## License

MIT License
