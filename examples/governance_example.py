"""
Example demonstrating the Governance Read API functionality.

This script shows how to use the Sui Python SDK to query governance information
including validator details, system state, staking data, and APY information.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import sui_py
sys.path.insert(0, str(Path(__file__).parent.parent))

from sui_py import SuiClient


async def main():
    """Demonstrate Governance Read API functionality."""
    
    # Initialize the client with testnet
    async with SuiClient("testnet") as client:
        print("🚀 Connected to Sui testnet")
        print(f"   Endpoint: {client.endpoint}")
        print()
        
        try:
            # 1. Get reference gas price
            print("📊 Getting reference gas price...")
            gas_price = await client.governance_read.get_reference_gas_price()
            print(f"   Reference gas price: {gas_price}")
            print()
            
            # 2. Get committee information
            print("🏛️  Getting committee information...")
            committee_info = await client.governance_read.get_committee_info()
            print(f"   Current epoch: {committee_info.epoch}")
            print(f"   Number of validators: {len(committee_info.validators)}")
            print()
            
            # 3. Get latest system state
            print("🌐 Getting latest system state...")
            system_state = await client.governance_read.get_latest_sui_system_state()
            print(f"   Epoch: {system_state.epoch}")
            print(f"   Protocol version: {system_state.protocol_version}")
            print(f"   Active validators: {len(system_state.active_validators)}")
            print(f"   Total stake: {system_state.total_stake}")
            print(f"   Reference gas price: {system_state.reference_gas_price}")
            print(f"   Safe mode: {system_state.safe_mode}")
            print()
            
            # 4. Get validator APY information
            print("💰 Getting validator APY information...")
            validator_apys = await client.governance_read.get_validators_apy()
            print(f"   Epoch: {validator_apys.epoch}")
            print(f"   Number of validators with APY data: {len(validator_apys.apys)}")
            
            # Show top 5 validators by APY
            sorted_apys = sorted(validator_apys.apys, key=lambda x: x.apy, reverse=True)
            print("\n   Top 5 validators by APY:")
            for i, validator_apy in enumerate(sorted_apys[:5], 1):
                print(f"   {i}. {validator_apy.address} - {validator_apy.apy:.2f}%")
            print()
            
            # 5. Show some validator details
            print("👥 Validator details (first 3):")
            for i, validator in enumerate(system_state.active_validators[:3], 1):
                print(f"   {i}. {validator.name}")
                print(f"      Address: {validator.sui_address}")
                print(f"      Voting power: {validator.voting_power}")
                print(f"      Gas price: {validator.gas_price}")
                print(f"      Commission rate: {validator.commission_rate}")
                print(f"      Next epoch stake: {validator.next_epoch_stake}")
                print()
            
            # 6. Example of getting stakes for a specific address (optional)
            # Note: This would require a valid address that has stakes
            print("📋 Stake query example:")
            print("   To query stakes for a specific address, use:")
            print("   stakes = await client.governance_read.get_stakes('0x...')")
            print("   This will return all delegated stakes for that address.")
            print()
            
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            return
    
    print("✅ Governance Read API demonstration completed!")


if __name__ == "__main__":
    asyncio.run(main()) 