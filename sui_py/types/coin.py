"""
Coin-related types for Sui Coin Query API.

These types correspond to the coin-specific Component Schemas in the Sui JSON-RPC API.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass

from .base import SuiAddress, ObjectID, TransactionDigest


@dataclass
class Balance:
    """
    Represents coin balance information for an address.
    
    Corresponds to the Balance schema in the Sui API.
    """
    coin_type: str
    coin_object_count: int
    total_balance: str  # String representation of big integer
    locked_balance: Dict[str, Any]  # Locked balance information
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Balance":
        """Create a Balance from API response data."""
        return cls(
            coin_type=data["coinType"],
            coin_object_count=data["coinObjectCount"],
            total_balance=data["totalBalance"],
            locked_balance=data.get("lockedBalance", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Balance to dictionary format."""
        return {
            "coinType": self.coin_type,
            "coinObjectCount": self.coin_object_count,
            "totalBalance": self.total_balance,
            "lockedBalance": self.locked_balance
        }
    
    @property
    def total_balance_int(self) -> int:
        """Get total balance as integer."""
        return int(self.total_balance)
    
    def is_zero(self) -> bool:
        """Check if the balance is zero."""
        return self.total_balance_int == 0


@dataclass
class Coin:
    """
    Represents an individual coin object.
    
    Corresponds to the Coin schema in the Sui API.
    """
    coin_type: str
    coin_object_id: ObjectID
    version: str
    digest: str
    balance: str  # String representation of big integer
    previous_transaction: TransactionDigest
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Coin":
        """Create a Coin from API response data."""
        return cls(
            coin_type=data["coinType"],
            coin_object_id=ObjectID.from_str(data["coinObjectId"]),
            version=data["version"],
            digest=data["digest"],
            balance=data["balance"],
            previous_transaction=TransactionDigest.from_str(data["previousTransaction"])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Coin to dictionary format."""
        return {
            "coinType": self.coin_type,
            "coinObjectId": str(self.coin_object_id),
            "version": self.version,
            "digest": self.digest,
            "balance": self.balance,
            "previousTransaction": str(self.previous_transaction)
        }
    
    @property
    def balance_int(self) -> int:
        """Get balance as integer."""
        return int(self.balance)
    
    def is_zero(self) -> bool:
        """Check if the coin balance is zero."""
        return self.balance_int == 0


@dataclass
class SuiCoinMetadata:
    """
    Represents metadata for a coin type.
    
    Corresponds to the SuiCoinMetadata schema in the Sui API.
    """
    decimals: int
    name: str
    symbol: str
    description: str
    icon_url: Optional[str]
    id: Optional[ObjectID]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuiCoinMetadata":
        """Create SuiCoinMetadata from API response data."""
        return cls(
            decimals=data["decimals"],
            name=data["name"],
            symbol=data["symbol"],
            description=data["description"],
            icon_url=data.get("iconUrl"),
            id=ObjectID.from_str(data["id"]) if data.get("id") else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SuiCoinMetadata to dictionary format."""
        result = {
            "decimals": self.decimals,
            "name": self.name,
            "symbol": self.symbol,
            "description": self.description
        }
        
        if self.icon_url:
            result["iconUrl"] = self.icon_url
        if self.id:
            result["id"] = str(self.id)
            
        return result
    
    def format_amount(self, amount: int) -> float:
        """Format an amount according to the coin's decimal places."""
        return amount / (10 ** self.decimals)
    
    def parse_amount(self, formatted_amount: float) -> int:
        """Parse a formatted amount to the coin's base units."""
        return int(formatted_amount * (10 ** self.decimals))


@dataclass
class Supply:
    """
    Represents total supply information for a coin type.
    
    Corresponds to the Supply schema in the Sui API.
    """
    value: str  # String representation of big integer
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Supply":
        """Create Supply from API response data."""
        return cls(value=data["value"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Supply to dictionary format."""
        return {"value": self.value}
    
    @property
    def value_int(self) -> int:
        """Get supply value as integer."""
        return int(self.value)
    
    def format_with_metadata(self, metadata: SuiCoinMetadata) -> float:
        """Format supply value using coin metadata."""
        return metadata.format_amount(self.value_int) 