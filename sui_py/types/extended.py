"""
Extended API types for Sui blockchain.

These types correspond to the Extended API Component Schemas in the Sui JSON-RPC API.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from .base import SuiAddress, ObjectID, TransactionDigest, Base64


class EventType(str, Enum):
    """Event type enumeration."""
    MOVE_EVENT = "moveEvent"
    PUBLISH = "publish"
    TRANSFER_OBJECT = "transferObject"
    DELETE_OBJECT = "deleteObject"
    NEW_OBJECT = "newObject"
    EPOCH_CHANGE = "epochChange"
    CHECKPOINT = "checkpoint"


class ObjectDataOptions(str, Enum):
    """Object data options for queries."""
    SHOW_TYPE = "showType"
    SHOW_OWNER = "showOwner"
    SHOW_PREVIOUS_TRANSACTION = "showPreviousTransaction"
    SHOW_DISPLAY = "showDisplay"
    SHOW_CONTENT = "showContent"
    SHOW_BCS = "showBcs"
    SHOW_STORAGE_REBATE = "showStorageRebate"


@dataclass
class DynamicFieldName:
    """
    Represents a dynamic field name.
    
    Corresponds to the DynamicFieldName schema in the Sui API.
    """
    type: str
    value: Any
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DynamicFieldName":
        """Create a DynamicFieldName from API response data."""
        return cls(
            type=data["type"],
            value=data["value"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DynamicFieldName to dictionary format."""
        return {
            "type": self.type,
            "value": self.value
        }


@dataclass
class DynamicFieldInfo:
    """
    Represents dynamic field information.
    
    Corresponds to the DynamicFieldInfo schema in the Sui API.
    """
    name: DynamicFieldName
    bcs_name: str
    type: str
    object_type: str
    object_id: ObjectID
    version: int
    digest: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DynamicFieldInfo":
        """Create a DynamicFieldInfo from API response data."""
        return cls(
            name=DynamicFieldName.from_dict(data["name"]),
            bcs_name=data["bcsName"],
            type=data["type"],
            object_type=data["objectType"],
            object_id=ObjectID.from_str(data["objectId"]),
            version=data["version"],
            digest=data["digest"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DynamicFieldInfo to dictionary format."""
        return {
            "name": self.name.to_dict(),
            "bcsName": self.bcs_name,
            "type": self.type,
            "objectType": self.object_type,
            "objectId": str(self.object_id),
            "version": self.version,
            "digest": self.digest
        }


@dataclass
class ObjectOwner:
    """
    Represents object ownership information.
    
    Can be AddressOwner, ObjectOwner, or Shared.
    """
    owner_type: str
    address: Optional[SuiAddress] = None
    object_id: Optional[ObjectID] = None
    initial_shared_version: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], str]) -> "ObjectOwner":
        """Create an ObjectOwner from API response data."""
        if isinstance(data, str):
            # Handle simple string cases like "Immutable"
            return cls(owner_type=data)
        
        if "AddressOwner" in data:
            return cls(
                owner_type="AddressOwner",
                address=SuiAddress.from_str(data["AddressOwner"])
            )
        elif "ObjectOwner" in data:
            return cls(
                owner_type="ObjectOwner",
                object_id=ObjectID.from_str(data["ObjectOwner"])
            )
        elif "Shared" in data:
            return cls(
                owner_type="Shared",
                initial_shared_version=data["Shared"]["initial_shared_version"]
            )
        else:
            # Handle other cases like "Immutable"
            return cls(owner_type=str(data))
    
    def to_dict(self) -> Union[Dict[str, Any], str]:
        """Convert ObjectOwner to dictionary format."""
        if self.owner_type == "AddressOwner" and self.address:
            return {"AddressOwner": str(self.address)}
        elif self.owner_type == "ObjectOwner" and self.object_id:
            return {"ObjectOwner": str(self.object_id)}
        elif self.owner_type == "Shared" and self.initial_shared_version is not None:
            return {"Shared": {"initial_shared_version": self.initial_shared_version}}
        else:
            return self.owner_type


@dataclass
class SuiObjectData:
    """
    Represents Sui object data.
    
    Corresponds to the SuiObjectData schema in the Sui API.
    """
    object_id: ObjectID
    version: int
    digest: str
    type: Optional[str] = None
    owner: Optional[ObjectOwner] = None
    previous_transaction: Optional[TransactionDigest] = None
    storage_rebate: Optional[int] = None
    display: Optional[Dict[str, Any]] = None
    content: Optional[Dict[str, Any]] = None
    bcs: Optional[Base64] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuiObjectData":
        """Create a SuiObjectData from API response data."""
        return cls(
            object_id=ObjectID.from_str(data["objectId"]),
            version=data["version"],
            digest=data["digest"],
            type=data.get("type"),
            owner=ObjectOwner.from_dict(data["owner"]) if data.get("owner") else None,
            previous_transaction=TransactionDigest.from_str(data["previousTransaction"]) if data.get("previousTransaction") else None,
            storage_rebate=data.get("storageRebate"),
            display=data.get("display"),
            content=data.get("content"),
            bcs=Base64.from_str(data["bcs"]) if data.get("bcs") else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SuiObjectData to dictionary format."""
        result = {
            "objectId": str(self.object_id),
            "version": self.version,
            "digest": self.digest
        }
        
        if self.type:
            result["type"] = self.type
        if self.owner:
            result["owner"] = self.owner.to_dict()
        if self.previous_transaction:
            result["previousTransaction"] = str(self.previous_transaction)
        if self.storage_rebate is not None:
            result["storageRebate"] = self.storage_rebate
        if self.display:
            result["display"] = self.display
        if self.content:
            result["content"] = self.content
        if self.bcs:
            result["bcs"] = str(self.bcs)
            
        return result


@dataclass
class SuiObjectResponse:
    """
    Represents a Sui object response.
    
    Corresponds to the SuiObjectResponse schema in the Sui API.
    """
    data: Optional[SuiObjectData] = None
    error: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuiObjectResponse":
        """Create a SuiObjectResponse from API response data."""
        return cls(
            data=SuiObjectData.from_dict(data["data"]) if data.get("data") else None,
            error=data.get("error")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SuiObjectResponse to dictionary format."""
        result = {}
        
        if self.data:
            result["data"] = self.data.to_dict()
        if self.error:
            result["error"] = self.error
            
        return result
    
    def is_success(self) -> bool:
        """Check if the response is successful."""
        return self.data is not None and self.error is None


@dataclass
class SuiEvent:
    """
    Represents a Sui event.
    
    Corresponds to the SuiEvent schema in the Sui API.
    """
    id: Dict[str, Any]  # EventID
    package_id: ObjectID
    transaction_module: str
    sender: SuiAddress
    type: str
    parsed_json: Optional[Dict[str, Any]] = None
    bcs: Optional[Base64] = None
    timestamp_ms: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuiEvent":
        """Create a SuiEvent from API response data."""
        return cls(
            id=data["id"],
            package_id=ObjectID.from_str(data["packageId"]),
            transaction_module=data["transactionModule"],
            sender=SuiAddress.from_str(data["sender"]),
            type=data["type"],
            parsed_json=data.get("parsedJson"),
            bcs=Base64.from_str(data["bcs"]) if data.get("bcs") else None,
            timestamp_ms=data.get("timestampMs")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SuiEvent to dictionary format."""
        result = {
            "id": self.id,
            "packageId": str(self.package_id),
            "transactionModule": self.transaction_module,
            "sender": str(self.sender),
            "type": self.type
        }
        
        if self.parsed_json:
            result["parsedJson"] = self.parsed_json
        if self.bcs:
            result["bcs"] = str(self.bcs)
        if self.timestamp_ms is not None:
            result["timestampMs"] = self.timestamp_ms
            
        return result


@dataclass
class TransactionBlockResponseOptions:
    """
    Options for transaction block response data.
    """
    show_input: bool = False
    show_raw_input: bool = False
    show_effects: bool = False
    show_events: bool = False
    show_object_changes: bool = False
    show_balance_changes: bool = False
    
    def to_dict(self) -> Dict[str, bool]:
        """Convert to dictionary format for API calls."""
        return {
            "showInput": self.show_input,
            "showRawInput": self.show_raw_input,
            "showEffects": self.show_effects,
            "showEvents": self.show_events,
            "showObjectChanges": self.show_object_changes,
            "showBalanceChanges": self.show_balance_changes
        }


@dataclass
class SuiTransactionBlock:
    """
    Represents a Sui transaction block.
    
    Corresponds to the SuiTransactionBlock schema in the Sui API.
    """
    data: Dict[str, Any]
    tx_signatures: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuiTransactionBlock":
        """Create a SuiTransactionBlock from API response data."""
        return cls(
            data=data["data"],
            tx_signatures=data["txSignatures"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SuiTransactionBlock to dictionary format."""
        return {
            "data": self.data,
            "txSignatures": self.tx_signatures
        }


@dataclass
class SuiTransactionBlockResponse:
    """
    Represents a Sui transaction block response.
    
    Corresponds to the SuiTransactionBlockResponse schema in the Sui API.
    """
    digest: TransactionDigest
    transaction: Optional[SuiTransactionBlock] = None
    raw_transaction: Optional[Base64] = None
    effects: Optional[Dict[str, Any]] = None
    events: Optional[List[SuiEvent]] = None
    object_changes: Optional[List[Dict[str, Any]]] = None
    balance_changes: Optional[List[Dict[str, Any]]] = None
    timestamp_ms: Optional[int] = None
    confirmed_local_execution: Optional[bool] = None
    checkpoint: Optional[int] = None
    errors: Optional[List[str]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuiTransactionBlockResponse":
        """Create a SuiTransactionBlockResponse from API response data."""
        return cls(
            digest=TransactionDigest.from_str(data["digest"]),
            transaction=SuiTransactionBlock.from_dict(data["transaction"]) if data.get("transaction") else None,
            raw_transaction=Base64.from_str(data["rawTransaction"]) if data.get("rawTransaction") else None,
            effects=data.get("effects"),
            events=[SuiEvent.from_dict(event) for event in data["events"]] if data.get("events") else None,
            object_changes=data.get("objectChanges"),
            balance_changes=data.get("balanceChanges"),
            timestamp_ms=data.get("timestampMs"),
            confirmed_local_execution=data.get("confirmedLocalExecution"),
            checkpoint=data.get("checkpoint"),
            errors=data.get("errors")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SuiTransactionBlockResponse to dictionary format."""
        result = {"digest": str(self.digest)}
        
        if self.transaction:
            result["transaction"] = self.transaction.to_dict()
        if self.raw_transaction:
            result["rawTransaction"] = str(self.raw_transaction)
        if self.effects:
            result["effects"] = self.effects
        if self.events:
            result["events"] = [event.to_dict() for event in self.events]
        if self.object_changes:
            result["objectChanges"] = self.object_changes
        if self.balance_changes:
            result["balanceChanges"] = self.balance_changes
        if self.timestamp_ms is not None:
            result["timestampMs"] = self.timestamp_ms
        if self.confirmed_local_execution is not None:
            result["confirmedLocalExecution"] = self.confirmed_local_execution
        if self.checkpoint is not None:
            result["checkpoint"] = self.checkpoint
        if self.errors:
            result["errors"] = self.errors
            
        return result


# Query filter types for convenience
@dataclass
class EventFilter:
    """Helper class for building event query filters."""
    
    @staticmethod
    def by_package(package_id: str) -> Dict[str, Any]:
        """Filter events by package ID."""
        return {"Package": package_id}
    
    @staticmethod
    def by_module(package_id: str, module_name: str) -> Dict[str, Any]:
        """Filter events by module."""
        return {"MoveEventModule": {"package": package_id, "module": module_name}}
    
    @staticmethod
    def by_event_type(event_type: str) -> Dict[str, Any]:
        """Filter events by event type."""
        return {"MoveEventType": event_type}
    
    @staticmethod
    def by_sender(sender: str) -> Dict[str, Any]:
        """Filter events by sender address."""
        return {"Sender": sender}
    
    @staticmethod
    def by_transaction(digest: str) -> Dict[str, Any]:
        """Filter events by transaction digest."""
        return {"Transaction": digest}
    
    @staticmethod
    def by_time_range(start_time: int, end_time: int) -> Dict[str, Any]:
        """Filter events by time range."""
        return {"TimeRange": {"start_time": start_time, "end_time": end_time}}


@dataclass
class TransactionFilter:
    """Helper class for building transaction query filters."""
    
    @staticmethod
    def by_checkpoint(checkpoint: int) -> Dict[str, Any]:
        """Filter transactions by checkpoint."""
        return {"Checkpoint": checkpoint}
    
    @staticmethod
    def by_move_function(package_id: str, module: str, function: str) -> Dict[str, Any]:
        """Filter transactions by Move function call."""
        return {
            "MoveFunction": {
                "package": package_id,
                "module": module,
                "function": function
            }
        }
    
    @staticmethod
    def by_input_object(object_id: str) -> Dict[str, Any]:
        """Filter transactions by input object."""
        return {"InputObject": object_id}
    
    @staticmethod
    def by_changed_object(object_id: str) -> Dict[str, Any]:
        """Filter transactions by changed object."""
        return {"ChangedObject": object_id}
    
    @staticmethod
    def by_from_address(address: str) -> Dict[str, Any]:
        """Filter transactions by sender address."""
        return {"FromAddress": address}
    
    @staticmethod
    def by_to_address(address: str) -> Dict[str, Any]:
        """Filter transactions by recipient address."""
        return {"ToAddress": address} 