# Governance Read API

The Governance Read API provides access to validator information, system state, staking data, and other governance-related information on the Sui blockchain.

## Overview

The `GovernanceReadClient` implements all governance-related read RPC methods from the Sui JSON-RPC API, allowing you to query:

- Committee information
- System state
- Reference gas prices
- Validator APY data
- Staking information

## Usage

### Basic Setup

```python
from sui_py import SuiClient

# Initialize client
async with SuiClient("mainnet") as client:
    # Access governance read methods
    governance = client.governance_read
```

### Available Methods

#### `get_reference_gas_price()`

Get the current reference gas price for the network.

```python
gas_price = await client.governance_read.get_reference_gas_price()
print(f"Reference gas price: {gas_price}")
```

**Returns:** `str` - The reference gas price as a string

#### `get_committee_info(epoch=None)`

Get committee information for the specified epoch (or current epoch if not specified).

```python
# Get current epoch committee info
committee = await client.governance_read.get_committee_info()
print(f"Epoch: {committee.epoch}")
print(f"Validators: {len(committee.validators)}")

# Get specific epoch committee info
committee_749 = await client.governance_read.get_committee_info("749")
```

**Parameters:**
- `epoch` (Optional[str]): The epoch to query. If None, returns current epoch.

**Returns:** `CommitteeInfo` - Contains epoch and validator information

#### `get_latest_sui_system_state()`

Get comprehensive system state information.

```python
system_state = await client.governance_read.get_latest_sui_system_state()
print(f"Epoch: {system_state.epoch}")
print(f"Protocol version: {system_state.protocol_version}")
print(f"Active validators: {len(system_state.active_validators)}")
print(f"Total stake: {system_state.total_stake}")
print(f"Safe mode: {system_state.safe_mode}")
```

**Returns:** `SuiSystemStateSummary` - Comprehensive system state data

#### `get_validators_apy()`

Get Annual Percentage Yield (APY) information for all validators.

```python
validator_apys = await client.governance_read.get_validators_apy()
print(f"Epoch: {validator_apys.epoch}")

# Sort validators by APY
sorted_validators = sorted(validator_apys.apys, key=lambda x: x.apy, reverse=True)
for validator in sorted_validators[:5]:  # Top 5
    print(f"{validator.address}: {validator.apy:.2f}%")
```

**Returns:** `ValidatorApys` - Contains APY data for all validators

#### `get_stakes(owner)`

Get all delegated stakes owned by an address.

```python
stakes = await client.governance_read.get_stakes("0x123...")
for stake in stakes:
    print(f"Validator: {stake.validator_address}")
    print(f"Staking pool: {stake.staking_pool}")
    print(f"Number of stakes: {len(stake.stakes)}")
```

**Parameters:**
- `owner` (Union[str, SuiAddress]): The owner address to query

**Returns:** `List[DelegatedStake]` - List of delegated stake objects

#### `get_stakes_by_ids(staked_sui_ids)`

Get delegated stakes by their specific staked SUI object IDs.

```python
stake_ids = ["0x123...", "0x456..."]
stakes = await client.governance_read.get_stakes_by_ids(stake_ids)
```

**Parameters:**
- `staked_sui_ids` (List[Union[str, ObjectID]]): List of staked SUI object IDs

**Returns:** `List[DelegatedStake]` - List of delegated stake objects

## Data Types

### `CommitteeInfo`

```python
@dataclass(frozen=True)
class CommitteeInfo:
    epoch: str
    validators: List[List[str]]  # List of [public_key, stake] pairs
```

### `SuiSystemStateSummary`

Contains comprehensive system state information including:
- Epoch and protocol information
- Validator data
- Staking pool information
- Storage fund details
- Safe mode status
- Subsidy information

### `ValidatorApys`

```python
@dataclass(frozen=True)
class ValidatorApys:
    apys: List[ValidatorApy]
    epoch: str

@dataclass(frozen=True)
class ValidatorApy:
    address: SuiAddress
    apy: float
```

### `DelegatedStake`

```python
@dataclass(frozen=True)
class DelegatedStake:
    stakes: List[StakeObject]
    staking_pool: str
    validator_address: str
```

### `StakeObject`

```python
@dataclass(frozen=True)
class StakeObject:
    staked_sui_id: ObjectID
    stake_request_epoch: str
    stake_active_epoch: str
    principal: str
    status: str
```

### `SuiValidatorSummary`

Contains detailed validator information including:
- Basic info (name, description, URLs)
- Network addresses and public keys
- Staking and rewards data
- Commission rates and gas prices
- Next epoch information

## Example: Complete Governance Information Query

```python
import asyncio
from sui_py import SuiClient

async def analyze_governance():
    async with SuiClient("mainnet") as client:
        # Get system overview
        system_state = await client.governance_read.get_latest_sui_system_state()
        gas_price = await client.governance_read.get_reference_gas_price()
        
        print(f"=== Sui Network Overview ===")
        print(f"Epoch: {system_state.epoch}")
        print(f"Protocol Version: {system_state.protocol_version}")
        print(f"Active Validators: {len(system_state.active_validators)}")
        print(f"Total Stake: {system_state.total_stake}")
        print(f"Reference Gas Price: {gas_price}")
        print(f"Safe Mode: {system_state.safe_mode}")
        
        # Get validator APY data
        validator_apys = await client.governance_read.get_validators_apy()
        sorted_apys = sorted(validator_apys.apys, key=lambda x: x.apy, reverse=True)
        
        print(f"\n=== Top 5 Validators by APY ===")
        for i, validator_apy in enumerate(sorted_apys[:5], 1):
            validator = next(
                (v for v in system_state.active_validators 
                 if v.sui_address == str(validator_apy.address)), 
                None
            )
            name = validator.name if validator else "Unknown"
            print(f"{i}. {name} ({validator_apy.address})")
            print(f"   APY: {validator_apy.apy:.2f}%")
            if validator:
                print(f"   Commission: {validator.commission_rate}")
                print(f"   Voting Power: {validator.voting_power}")

asyncio.run(analyze_governance())
```

## Error Handling

All methods may raise:
- `SuiRpcError`: For RPC-level errors
- `SuiNetworkError`: For network-related errors  
- `SuiTimeoutError`: For timeout errors
- `SuiValidationError`: For address validation errors

```python
from sui_py.exceptions import SuiRpcError, SuiValidationError

try:
    stakes = await client.governance_read.get_stakes("invalid_address")
except SuiValidationError as e:
    print(f"Invalid address format: {e}")
except SuiRpcError as e:
    print(f"RPC error: {e}")
```

## Network Compatibility

The Governance Read API works with all Sui networks:
- Mainnet
- Testnet  
- Devnet
- Localnet

Simply specify the network when creating the client:

```python
# Different networks
async with SuiClient("mainnet") as client: ...
async with SuiClient("testnet") as client: ...
async with SuiClient("devnet") as client: ...
async with SuiClient("localnet") as client: ...
``` 