"""
Configuration for the Coffee Club Event Indexer.

This module contains all configuration settings for the coffee club event indexer,
including network settings, database configuration, coffee club contract addresses,
and coffee machine integration settings.
"""

import os
from dataclasses import dataclass
from typing import List

from sui_py.constants import NETWORK_ENDPOINTS


@dataclass
class CoffeeClubContract:
    """Configuration for the coffee club contract."""
    package_id: str


@dataclass
class CoffeeMachine:
    """Configuration for coffee machine integration."""
    mac_address: str
    controller_path: str
    enabled: bool = True


@dataclass
class IndexerConfig:
    """Main coffee club indexer configuration."""
    # Network settings
    network: str
    rpc_url: str
    
    # Contract configuration
    coffee_club_contract: CoffeeClubContract
    
    # Coffee machine configuration
    coffee_machine: CoffeeMachine
    
    # Database configuration (Prisma uses DATABASE_URL environment variable)
    database_url: str
    
    # Indexer settings
    polling_interval_ms: int = 5000  # 5 seconds (matching TypeScript)
    error_retry_interval_ms: int = 30000  # 30 seconds
    batch_size: int = 100
    max_retries: int = 3
    retry_delay_ms: int = 5000  # 5 seconds
    
    # Valid coffee types that match the Move enum variants
    valid_coffee_types: List[str] = None
    
    def __post_init__(self):
        if self.valid_coffee_types is None:
            self.valid_coffee_types = [
                'espresso',
                'americano', 
                'doppio',
                'long',
                'coffee',
                'hotwater'
            ]


def get_config() -> IndexerConfig:
    """Get the coffee club indexer configuration from environment variables or defaults."""
    
    # Network configuration
    network = os.getenv("SUI_NETWORK", "testnet")
    rpc_url = os.getenv("SUI_RPC_URL", NETWORK_ENDPOINTS.get(network, NETWORK_ENDPOINTS["mainnet"]))
    
    # Coffee club contract configuration
    package_id = os.getenv(
        "PACKAGE_ID", 
        "0x7072e9cc59fe353374e0ef5822e98165ec441bcdcb1cfa10f89b40c9285965f3" # Replace with actual coffee club package ID
    )
    
    # Coffee machine configuration
    mac_address = os.getenv("MAC_ADDRESS", "00:00:00:00:00:00")
    controller_path = os.getenv(
        "CONTROLLER_PATH", 
        "../delonghi_controller/src/delonghi_controller.py"
    )
    machine_enabled = os.getenv("COFFEE_MACHINE_ENABLED", "true").lower() == "true"
    
    # Database configuration (Prisma reads DATABASE_URL automatically)
    database_url = os.getenv("DATABASE_URL", "file:./coffee_club.db")
    
    # Indexer settings
    polling_interval = int(os.getenv("POLLING_INTERVAL_MS", "5000"))
    error_retry_interval = int(os.getenv("ERROR_RETRY_INTERVAL_MS", "30000"))
    batch_size = int(os.getenv("BATCH_SIZE", "100"))
    max_retries = int(os.getenv("MAX_RETRIES", "3"))
    retry_delay = int(os.getenv("RETRY_DELAY_MS", "5000"))
    
    return IndexerConfig(
        network=network,
        rpc_url=rpc_url,
        coffee_club_contract=CoffeeClubContract(package_id=package_id),
        coffee_machine=CoffeeMachine(
            mac_address=mac_address,
            controller_path=controller_path,
            enabled=machine_enabled
        ),
        database_url=database_url,
        polling_interval_ms=polling_interval,
        error_retry_interval_ms=error_retry_interval,
        batch_size=batch_size,
        max_retries=max_retries,
        retry_delay_ms=retry_delay
    )


# Global configuration instance
CONFIG = get_config()

# Set DATABASE_URL environment variable for Prisma
os.environ["DATABASE_URL"] = CONFIG.database_url 