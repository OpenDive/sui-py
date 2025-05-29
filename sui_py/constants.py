"""
Constants for Sui network configuration and API endpoints.
"""

from typing import Dict

# Network endpoints
NETWORK_ENDPOINTS: Dict[str, str] = {
    "mainnet": "https://fullnode.mainnet.sui.io:443",
    "testnet": "https://fullnode.testnet.sui.io:443", 
    "devnet": "https://fullnode.devnet.sui.io:443",
    "localnet": "http://127.0.0.1:9000",
}

# Default configuration
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0

# JSON-RPC constants
JSONRPC_VERSION = "2.0"

# Common coin types
SUI_COIN_TYPE = "0x2::sui::SUI" 