#!/usr/bin/env python3
"""
Read API Example for SuiPy SDK

This example demonstrates how to use the Read API to query blockchain state,
objects, transactions, checkpoints, and system information.

Usage:
    python3 examples/read_api_example.py [network]

Example:
    python3 examples/read_api_example.py testnet

Parameters:
    network: Network to connect to (mainnet, testnet, devnet, localnet)
             Defaults to 'testnet'

The example will demonstrate:
- Getting chain identifier and protocol configuration
- Fetching object information
- Querying transaction data
- Retrieving checkpoint information
- System information queries

TODO: Add examples for missing Read API methods:
TODO: - sui_tryMultiGetPastObjects (batch historical object queries)
TODO: - sui_verifyZkLoginSignature (zkLogin signature verification)
TODO: Add comprehensive error handling examples
TODO: Add examples with failed transactions and complex events
TODO: Add historical object version testing
TODO: Add performance testing scenarios
"""

import asyncio
import sys
from typing import Optional

from sui_py import SuiClient, SuiError, SuiRPCError
from sui_py.types import ReadObjectDataOptions


async def demonstrate_system_info(client: SuiClient):
    """Demonstrate system information queries."""
    print("=== System Information ===")
    
    try:
        # Get chain identifier
        chain_id = await client.read_api.get_chain_identifier()
        print(f"Chain ID: {chain_id}")
        
        # Get protocol configuration
        try:
            protocol_config = await client.read_api.get_protocol_config()
            print(f"Protocol Version: {protocol_config.version}")
            print(f"Max Transaction Size: {protocol_config.max_tx_size_bytes} bytes")
            print(f"Max Gas: {protocol_config.max_tx_gas}")
        except SuiRPCError as protocol_error:
            print(f"Protocol config error: {protocol_error}")
        
        # Get total transaction count
        total_txs = await client.read_api.get_total_transaction_blocks()
        print(f"Total Transactions: {total_txs:,}")
        
    except SuiError as e:
        print(f"Error getting system info: {e}")
    
    print()


async def demonstrate_checkpoint_queries(client: SuiClient):
    """Demonstrate checkpoint-related queries."""
    print("=== Checkpoint Information ===")
    
    try:
        # Get latest checkpoint sequence number
        latest_seq = await client.read_api.get_latest_checkpoint_sequence_number()
        print(f"Latest Checkpoint: {latest_seq}")
        
        # Get specific checkpoint
        try:
            checkpoint = await client.read_api.get_checkpoint(latest_seq)
            print(f"Checkpoint {checkpoint.sequence_number}:")
            print(f"  Epoch: {checkpoint.epoch}")
            print(f"  Digest: {checkpoint.digest}")
            print(f"  Timestamp: {checkpoint.timestamp_ms}")
            print(f"  Transactions: {len(checkpoint.transactions)}")
        except Exception as checkpoint_error:
            print(f"Checkpoint fetch error: {checkpoint_error}")
        
        # Get recent checkpoints
        try:
            checkpoints_page = await client.read_api.get_checkpoints(limit=3, descending=True)
            print(f"\nRecent Checkpoints ({len(checkpoints_page.data)}):")
            for cp in checkpoints_page.data:
                print(f"  #{cp.sequence_number} - Epoch {cp.epoch} - {len(cp.transactions)} txs")
        except Exception as checkpoints_error:
            print(f"Checkpoints page error: {checkpoints_error}")
        
    except Exception as e:
        print(f"Error getting checkpoint info: {e}")
    
    print()


async def demonstrate_object_queries(client: SuiClient):
    """Demonstrate object-related queries."""
    print("=== Object Queries ===")
    
    # Use a well-known object ID (Sui system state object)
    system_state_id = "0x0000000000000000000000000000000000000000000000000000000000000005"
    
    # TODO: Add more system object examples:
    # TODO: - Clock object: 0x0000000000000000000000000000000000000000000000000000000000000006
    # TODO: - Random object: 0x0000000000000000000000000000000000000000000000000000000000000008
    # TODO: Test with different object types (coins, NFTs, packages)
    # TODO: Add error handling examples with invalid object IDs
    
    try:
        # Basic object query
        print("Basic object query:")
        obj_response = await client.read_api.get_object(system_state_id)
        if obj_response.data:
            print(f"  Object ID: {obj_response.data.object_id}")
            print(f"  Version: {obj_response.data.version}")
            print(f"  Digest: {obj_response.data.digest}")
        else:
            print(f"  Error: {obj_response.error}")
        
        # Query with options
        print("\nDetailed object query:")
        options = ReadObjectDataOptions(
            show_type=True,
            show_owner=True,
            show_content=True
        )
        detailed_response = await client.read_api.get_object(system_state_id, options=options)
        if detailed_response.data:
            data = detailed_response.data
            print(f"  Object ID: {data.object_id}")
            print(f"  Type: {data.type}")
            print(f"  Owner: {data.owner.owner_type if data.owner else 'None'}")
            print(f"  Has Content: {data.content is not None}")
        
        # Multi-get objects
        print("\nMulti-object query:")
        object_ids = [system_state_id]  # Add more IDs if available
        multi_response = await client.read_api.multi_get_objects(object_ids, options=options)
        print(f"  Retrieved {len(multi_response)} objects")
        for i, response in enumerate(multi_response):
            if response.data:
                print(f"    Object {i+1}: {response.data.object_id} (v{response.data.version})")
            else:
                print(f"    Object {i+1}: Error - {response.error}")
        
        # TODO: Add historical object query example
        # TODO: Find an object with version > 1 and test try_get_past_object
        # TODO: Example:
        # TODO: past_obj = await client.read_api.try_get_past_object(object_id, version=1)
        
        # TODO: Add multi-past-object query example (when implemented)
        # TODO: past_objects = [{"objectId": "0x...", "version": 1}, {"objectId": "0x...", "version": 2}]
        # TODO: multi_past = await client.read_api.try_multi_get_past_objects(past_objects)
        
    except Exception as e:
        print(f"Error in object queries: {e}")
    
    print()


async def demonstrate_transaction_queries(client: SuiClient):
    """Demonstrate transaction-related queries."""
    print("=== Transaction Queries ===")
    
    # TODO: Add examples for different transaction types:
    # TODO: - Failed transactions (status != "success")
    # TODO: - Transactions with many events
    # TODO: - Complex smart contract interactions
    # TODO: - Package publication transactions
    # TODO: Add error handling for invalid transaction digests
    
    try:
        # Get a recent checkpoint to find transaction digests
        checkpoints_page = await client.read_api.get_checkpoints(limit=1, descending=True)
        if not checkpoints_page.data or not checkpoints_page.data[0].transactions:
            print("No recent transactions found")
            return
        
        # Get the first transaction from the latest checkpoint
        tx_digest = checkpoints_page.data[0].transactions[0]
        print(f"Querying transaction: {tx_digest}")
        
        # Basic transaction query with effects
        from sui_py.types import TransactionBlockResponseOptions
        options = TransactionBlockResponseOptions(show_effects=True)
        tx_response = await client.read_api.get_transaction_block(tx_digest, options=options)
        print(f"  Transaction found: {tx_response.digest}")
        print(f"  Timestamp: {tx_response.timestamp_ms}")
        if tx_response.effects:
            # Extract status from the status dictionary
            status = tx_response.effects.status
            if isinstance(status, dict):
                status_value = status.get("status", "Unknown")
            else:
                status_value = str(status)
            print(f"  Status: {status_value}")
            
            # Extract gas used from gas_used dictionary
            gas_used = tx_response.effects.gas_used
            if isinstance(gas_used, dict):
                computation_cost = int(gas_used.get("computationCost", 0))
                storage_cost = int(gas_used.get("storageCost", 0))
                storage_rebate = int(gas_used.get("storageRebate", 0))
                total_gas = computation_cost + storage_cost - storage_rebate
                print(f"  Gas Used: {total_gas} (computation: {computation_cost}, storage: {storage_cost}, rebate: {storage_rebate})")
            else:
                print(f"  Gas Used: {gas_used}")
        
        # Get events for this transaction
        events = await client.read_api.get_events(tx_digest)
        print(f"  Events: {len(events)}")
        
        # Multi-get transactions
        if len(checkpoints_page.data[0].transactions) > 1:
            tx_digests = checkpoints_page.data[0].transactions[:3]  # First 3 transactions
            multi_tx_response = await client.read_api.multi_get_transaction_blocks(tx_digests, options=options)
            print(f"\nMulti-transaction query: {len(multi_tx_response)} transactions")
            for i, tx in enumerate(multi_tx_response):
                if tx.effects and isinstance(tx.effects.status, dict):
                    status = tx.effects.status.get("status", "Unknown")
                elif tx.effects:
                    status = str(tx.effects.status)
                else:
                    status = "Unknown"
                print(f"    Transaction {i+1}: {status}")
        
        # TODO: Add examples for analyzing transaction patterns:
        # TODO: - Scan multiple checkpoints for failed transactions
        # TODO: - Find transactions with specific event types
        # TODO: - Analyze gas usage patterns across transactions
        # TODO: - Test transaction queries with very old digests
        
    except Exception as e:
        print(f"Error in transaction queries: {e}")
    
    print()


# TODO: Add new demonstration functions:

# TODO: async def demonstrate_error_handling(client: SuiClient):
# TODO:     """Demonstrate comprehensive error handling scenarios."""
# TODO:     # Test invalid object IDs, transaction digests, checkpoint IDs
# TODO:     # Test network timeout scenarios
# TODO:     # Test malformed response handling

# TODO: async def demonstrate_historical_queries(client: SuiClient):
# TODO:     """Demonstrate historical object and transaction queries."""
# TODO:     # Find objects with version history
# TODO:     # Test try_get_past_object with real data
# TODO:     # Test try_multi_get_past_objects (when implemented)

# TODO: async def demonstrate_advanced_features(client: SuiClient):
# TODO:     """Demonstrate advanced Read API features."""
# TODO:     # Test zkLogin signature verification (when implemented)
# TODO:     # Test complex pagination scenarios
# TODO:     # Test performance with large datasets

# TODO: async def demonstrate_real_world_patterns(client: SuiClient):
# TODO:     """Demonstrate real-world usage patterns."""
# TODO:     # Wallet balance tracking
# TODO:     # NFT metadata retrieval
# TODO:     # Transaction history analysis
# TODO:     # Smart contract event monitoring

async def main():
    """Main example function."""
    # Get network from command line argument
    network = sys.argv[1] if len(sys.argv) > 1 else "testnet"
    
    print(f"Read API Example - Connecting to {network}")
    print("=" * 50)
    
    try:
        async with SuiClient(network) as client:
            print(f"Connected to: {client.endpoint}")
            print()
            
            # Demonstrate different Read API capabilities
            await demonstrate_system_info(client)
            await demonstrate_checkpoint_queries(client)
            await demonstrate_object_queries(client)
            await demonstrate_transaction_queries(client)
            
            # TODO: Add calls to new demonstration functions:
            # TODO: await demonstrate_error_handling(client)
            # TODO: await demonstrate_historical_queries(client)
            # TODO: await demonstrate_advanced_features(client)
            # TODO: await demonstrate_real_world_patterns(client)
            
            print("=== Example Complete ===")
            print("\nKey Takeaways:")
            print("- Read API provides comprehensive blockchain state access")
            print("- Object queries support flexible data options")
            print("- Checkpoint data enables blockchain history analysis")
            print("- Transaction queries provide detailed execution information")
            print("- System info queries help understand network configuration")
            
            print("\nTODO: Additional features to implement and test:")
            print("- Historical object queries (try_get_past_object)")
            print("- Batch historical queries (try_multi_get_past_objects)")
            print("- ZkLogin signature verification")
            print("- Comprehensive error handling examples")
            print("- Performance testing with large datasets")
            print("- Real-world integration patterns")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
