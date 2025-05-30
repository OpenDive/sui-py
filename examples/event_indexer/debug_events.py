#!/usr/bin/env python3
"""
Debug script to check what events are available from the swap package.
"""

import asyncio
import logging
from sui_py import SuiClient, EventFilter
from config import CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_events():
    """Check what events are available from the swap package."""
    client = SuiClient(CONFIG.rpc_url)
    await client.connect()
    
    try:
        # Query any events from this package
        logger.info(f"Checking events from package: {CONFIG.swap_contract.package_id}")
        
        # Try different approaches
        try:
            # Test 1: Try querying lock events (we know these work)
            print(f'\n🔍 Test 1: Checking lock events (known to work)...')
            lock_events = await client.extended_api.query_events(
                EventFilter.by_module(CONFIG.swap_contract.package_id, "lock"),
                limit=5
            )
            print(f'Lock module events: {len(lock_events.data)}')
            if lock_events.data:
                print(f'First lock event type: {lock_events.data[0].type}')
        except Exception as e:
            print(f'Error querying lock events: {e}')
        
        try:
            # Test 2: Try querying shared events
            print(f'\n🔍 Test 2: Checking shared events...')
            shared_events = await client.extended_api.query_events(
                EventFilter.by_module(CONFIG.swap_contract.package_id, "shared"),
                limit=5
            )
            print(f'Shared module events: {len(shared_events.data)}')
            if shared_events.data:
                for event in shared_events.data:
                    print(f'  - {event.type}')
        except Exception as e:
            print(f'Error querying shared events: {e}')
        
        try:
            # Test 3: Try other possible module names
            print(f'\n🔍 Test 3: Checking other possible modules...')
            possible_modules = ["escrow", "swap", "amm", "pool"]
            for module in possible_modules:
                try:
                    events = await client.extended_api.query_events(
                        EventFilter.by_module(CONFIG.swap_contract.package_id, module),
                        limit=3
                    )
                    if events.data:
                        print(f'  {module}: {len(events.data)} events')
                        for event in events.data[:2]:  # Show first 2
                            print(f'    - {event.type}')
                except Exception as e:
                    print(f'  {module}: Error - {e}')
        except Exception as e:
            print(f'Error in test 3: {e}')
        
    except Exception as e:
        logger.error(f"General error: {e}")
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_events()) 