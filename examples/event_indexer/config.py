"""
Configuration for the SuiPy Event Indexer.

This module contains all configuration settings for the event indexer,
including network settings, database configuration, and contract addresses.
"""

import os
from dataclasses import dataclass
from typing import Optional

from sui_py.constants import NETWORK_ENDPOINTS


@dataclass
class SwapContract:
    """Configuration for the swap contract."""
    package_id: str


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    echo: bool = False


@dataclass
class IndexerConfig:
    """Main indexer configuration."""
    # Network settings
    network: str
    rpc_url: str
    
    # Contract configuration
    swap_contract: SwapContract
    
    # Database configuration
    database: DatabaseConfig
    
    # Indexer settings
    polling_interval_ms: int = 1000  # 1 second
    batch_size: int = 100
    max_retries: int = 3
    retry_delay_ms: int = 5000  # 5 seconds


# Default configuration
def get_config() -> IndexerConfig:
    """Get the indexer configuration from environment variables or defaults."""
    
    # Network configuration
    network = os.getenv("SUI_NETWORK", "mainnet")
    rpc_url = os.getenv("SUI_RPC_URL", NETWORK_ENDPOINTS.get(network, NETWORK_ENDPOINTS["mainnet"]))
    
    # Contract configuration
    swap_package_id = os.getenv(
        "SWAP_PACKAGE_ID", 
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"  # Example package ID
    )
    
    # Database configuration
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./indexer.db")
    db_echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    
    # Indexer settings
    polling_interval = int(os.getenv("POLLING_INTERVAL_MS", "1000"))
    batch_size = int(os.getenv("BATCH_SIZE", "100"))
    max_retries = int(os.getenv("MAX_RETRIES", "3"))
    retry_delay = int(os.getenv("RETRY_DELAY_MS", "5000"))
    
    return IndexerConfig(
        network=network,
        rpc_url=rpc_url,
        swap_contract=SwapContract(package_id=swap_package_id),
        database=DatabaseConfig(url=db_url, echo=db_echo),
        polling_interval_ms=polling_interval,
        batch_size=batch_size,
        max_retries=max_retries,
        retry_delay_ms=retry_delay
    )


# Global configuration instance
CONFIG = get_config() 