"""
Configuration for the SuiPy Event Indexer.

This module contains all configuration settings for the event indexer,
including network settings, database configuration, and contract addresses.
"""

import os
from dataclasses import dataclass

from sui_py.constants import NETWORK_ENDPOINTS


@dataclass
class SwapContract:
    """Configuration for the swap contract."""
    package_id: str


@dataclass
class IndexerConfig:
    """Main indexer configuration."""
    # Network settings
    network: str
    rpc_url: str
    
    # Contract configuration
    swap_contract: SwapContract
    
    # Database configuration (Prisma uses DATABASE_URL environment variable)
    database_url: str
    
    # Indexer settings
    polling_interval_ms: int = 1000  # 1 second
    batch_size: int = 100
    max_retries: int = 3
    retry_delay_ms: int = 5000  # 5 seconds


def get_config() -> IndexerConfig:
    """Get the indexer configuration from environment variables or defaults."""
    
    # Network configuration
    network = os.getenv("SUI_NETWORK", "testnet")
    rpc_url = os.getenv("SUI_RPC_URL", NETWORK_ENDPOINTS.get(network, NETWORK_ENDPOINTS["mainnet"]))
    
    # Contract configuration
    swap_package_id = os.getenv(
        "SWAP_PACKAGE_ID", 
        "0x052f4da5dddf486da555e6c6aea3818e8d8206931f74f7441be5417cf9eeb070"  # Example package ID
    )
    
    # Database configuration (Prisma reads DATABASE_URL automatically)
    database_url = os.getenv("DATABASE_URL", "file:./indexer.db")
    
    # Indexer settings
    polling_interval = int(os.getenv("POLLING_INTERVAL_MS", "1000"))
    batch_size = int(os.getenv("BATCH_SIZE", "100"))
    max_retries = int(os.getenv("MAX_RETRIES", "3"))
    retry_delay = int(os.getenv("RETRY_DELAY_MS", "5000"))
    
    return IndexerConfig(
        network=network,
        rpc_url=rpc_url,
        swap_contract=SwapContract(package_id=swap_package_id),
        database_url=database_url,
        polling_interval_ms=polling_interval,
        batch_size=batch_size,
        max_retries=max_retries,
        retry_delay_ms=retry_delay
    )


# Global configuration instance
CONFIG = get_config()

# Set DATABASE_URL environment variable for Prisma
os.environ["DATABASE_URL"] = CONFIG.database_url 