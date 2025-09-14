"""
Write API types for Sui blockchain.

These types correspond to the Write API Component Schemas in the Sui JSON-RPC API.
Implements response types for sui_executeTransactionBlock, sui_dryRunTransactionBlock,
and sui_devInspectTransactionBlock methods.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from .base import SuiAddress, ObjectID, TransactionDigest, Base64
from .extended import SuiEvent, SuiTransactionBlockResponse


class ExecuteTransactionRequestType(str, Enum):
    """
    Request type for transaction execution.
    
    From Sui API documentation:
    - WaitForEffectsCert: waits for TransactionEffectsCert and then return to client
    - WaitForLocalExecution: waits for TransactionEffectsCert and make sure the node 
      executed the transaction locally before returning
    """
    WAIT_FOR_EFFECTS_CERT = "WaitForEffectsCert"
    WAIT_FOR_LOCAL_EXECUTION = "WaitForLocalExecution"


@dataclass
class TransactionBlockResponseOptions:
    """
    Options for specifying the content to be returned in transaction responses.
    
    Corresponds to SuiTransactionBlockResponseOptions in Sui API.
    """
    show_input: bool = False
    show_raw_input: bool = False
    show_effects: bool = True
    show_events: bool = False
    show_object_changes: bool = False
    show_balance_changes: bool = False
    show_raw_effects: bool = False
    
    def to_dict(self) -> Dict[str, bool]:
        """Convert to dictionary format for RPC calls."""
        return {
            "showInput": self.show_input,
            "showRawInput": self.show_raw_input,
            "showEffects": self.show_effects,
            "showEvents": self.show_events,
            "showObjectChanges": self.show_object_changes,
            "showBalanceChanges": self.show_balance_changes,
            "showRawEffects": self.show_raw_effects,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransactionBlockResponseOptions":
        """Create from API response data."""
        return cls(
            show_input=data.get("showInput", False),
            show_raw_input=data.get("showRawInput", False),
            show_effects=data.get("showEffects", True),
            show_events=data.get("showEvents", False),
            show_object_changes=data.get("showObjectChanges", False),
            show_balance_changes=data.get("showBalanceChanges", False),
            show_raw_effects=data.get("showRawEffects", False),
        )


@dataclass
class BalanceChange:
    """
    Represents a balance change in a transaction.
    
    Corresponds to BalanceChange schema in Sui API.
    """
    amount: str  # The amount (negative = spending, positive = receiving)
    coin_type: str
    owner: str  # Owner of the balance change
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BalanceChange":
        """Create from API response data."""
        return cls(
            amount=data["amount"],
            coin_type=data["coinType"],
            owner=data["owner"]
        )


@dataclass
class ObjectChange:
    """
    Represents an object change in a transaction.
    
    Corresponds to ObjectChange schema in Sui API.
    """
    type: str  # Type of change (created, mutated, deleted, etc.)
    sender: Optional[str] = None
    owner: Optional[str] = None
    object_type: Optional[str] = None
    object_id: Optional[ObjectID] = None
    version: Optional[str] = None
    digest: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObjectChange":
        """Create from API response data."""
        return cls(
            type=data["type"],
            sender=data.get("sender"),
            owner=data.get("owner"),
            object_type=data.get("objectType"),
            object_id=ObjectID.from_str(data["objectId"]) if "objectId" in data else None,
            version=data.get("version"),
            digest=data.get("digest")
        )


@dataclass
class TransactionEffects:
    """
    Transaction execution effects.
    
    Corresponds to TransactionBlockEffects schema in Sui API.
    """
    status: Dict[str, Any]  # Execution status
    gas_used: Dict[str, Any]  # Gas cost summary
    transaction_digest: TransactionDigest
    created: Optional[List[Dict[str, Any]]] = None
    mutated: Optional[List[Dict[str, Any]]] = None
    deleted: Optional[List[Dict[str, Any]]] = None
    gas_object: Optional[Dict[str, Any]] = None
    events_digest: Optional[str] = None
    dependencies: Optional[List[str]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransactionEffects":
        """Create from API response data."""
        return cls(
            status=data["status"],
            gas_used=data["gasUsed"],
            transaction_digest=TransactionDigest.from_str(data["transactionDigest"]),
            created=data.get("created"),
            mutated=data.get("mutated"),
            deleted=data.get("deleted"),
            gas_object=data.get("gasObject"),
            events_digest=data.get("eventsDigest"),
            dependencies=data.get("dependencies")
        )


@dataclass
class DryRunTransactionBlockResponse:
    """
    Response from sui_dryRunTransactionBlock.
    
    Returns transaction execution effects without committing to chain.
    """
    effects: TransactionEffects
    events: List[SuiEvent]
    input: Optional[Dict[str, Any]] = None
    balance_changes: Optional[List[BalanceChange]] = None
    object_changes: Optional[List[ObjectChange]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DryRunTransactionBlockResponse":
        """Create from API response data."""
        return cls(
            effects=TransactionEffects.from_dict(data["effects"]),
            events=[SuiEvent.from_dict(event) for event in data.get("events", [])],
            input=data.get("input"),
            balance_changes=[BalanceChange.from_dict(bc) for bc in data.get("balanceChanges", [])],
            object_changes=[ObjectChange.from_dict(oc) for oc in data.get("objectChanges", [])]
        )


@dataclass
class DevInspectArgs:
    """
    Additional arguments for dev inspect transaction.
    
    Corresponds to DevInspectArgs schema in Sui API.
    """
    gas_budget: Optional[str] = None
    gas_objects: Optional[List[ObjectID]] = None
    gas_sponsor: Optional[SuiAddress] = None
    skip_checks: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for RPC calls."""
        result = {}
        if self.gas_budget is not None:
            result["gasBudget"] = self.gas_budget
        if self.gas_objects is not None:
            result["gasObjects"] = [str(obj_id) for obj_id in self.gas_objects]
        if self.gas_sponsor is not None:
            result["gasSponsor"] = str(self.gas_sponsor)
        if self.skip_checks is not None:
            result["skipChecks"] = self.skip_checks
        return result


@dataclass
class DevInspectResults:
    """
    Response from sui_devInspectTransactionBlock.
    
    Provides detailed results from development inspection.
    """
    effects: TransactionEffects
    events: List[SuiEvent]
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DevInspectResults":
        """Create from API response data."""
        return cls(
            effects=TransactionEffects.from_dict(data["effects"]),
            events=[SuiEvent.from_dict(event) for event in data.get("events", [])],
            results=data.get("results"),
            error=data.get("error")
        )