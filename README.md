# sui-py
SuiPy – a deliciously lightweight, high-performance Python SDK for the Sui blockchain

## Design Philosophy

- **Async-First**: Built for high-performance concurrent operations
- **Type-Safe**: Full type hints and structured data models (coming soon)
- **Lightweight**: Minimal dependencies, maximum performance

## Current Status

🚧 **In Development** - Currently implementing Coin Query API

### Async-First Design

This SDK is designed with async/await as the primary interface for optimal performance with I/O-bound blockchain operations. A synchronous wrapper may be added in the future based on user demand.

```python
# Async interface (current)
async with SuiClient("mainnet") as client:
    balance = await client.coin_query.get_balance(address)
    coins = await client.coin_query.get_all_coins(address)
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

### 🚧 Coming Soon
- Extended API (objects, events, transactions)
- Read API (checkpoints, protocol config)
- Transaction Builder API
- Write API (transaction execution)
- Typed data models (Address, ObjectID, etc.)

## Installation

```bash
pip install sui-py  # Coming soon
```

For development:
```bash
git clone https://github.com/your-org/sui-py
cd sui-py
pip install -r requirements.txt
```

## Quick Start

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

See the `examples/` directory for complete usage examples:
- `coin_query_example.py` - Comprehensive Coin Query API usage

## Contributing

This project is in active development. Contributions are welcome!

## License

MIT License
