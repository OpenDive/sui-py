"""
Read API types for Sui blockchain.

These types correspond to the Read API Component Schemas in the Sui JSON-RPC API.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from .base import SuiAddress, ObjectID, TransactionDigest, Base64


@dataclass
class ObjectDataOptions:
    """
    Options for specifying which object data to include in responses.
    
    Corresponds to the SuiObjectDataOptions schema in the Sui API.
    """
    show_type: bool = False
    show_owner: bool = False
    show_previous_transaction: bool = False
    show_display: bool = False
    show_content: bool = False
    show_bcs: bool = False
    show_storage_rebate: bool = False
    
    def to_dict(self) -> Dict[str, bool]:
        """Convert to dictionary format for API requests."""
        return {
            "showType": self.show_type,
            "showOwner": self.show_owner,
            "showPreviousTransaction": self.show_previous_transaction,
            "showDisplay": self.show_display,
            "showContent": self.show_content,
            "showBcs": self.show_bcs,
            "showStorageRebate": self.show_storage_rebate,
        }


@dataclass
class Checkpoint:
    """
    Represents a Sui checkpoint.
    
    Corresponds to the Checkpoint schema in the Sui API.
    """
    epoch: int
    sequence_number: int
    digest: str
    network_total_transactions: int
    previous_digest: Optional[str] = None
    epoch_rolling_gas_cost_summary: Optional[Dict[str, Any]] = None
    timestamp_ms: int = 0
    transactions: List[TransactionDigest] = None
    checkpoint_commitments: List[Dict[str, Any]] = None
    validator_signature: Optional[str] = None
    
    def __post_init__(self):
        if self.transactions is None:
            self.transactions = []
        if self.checkpoint_commitments is None:
            self.checkpoint_commitments = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        """Create a Checkpoint from API response data."""
        return cls(
            epoch=data["epoch"],
            sequence_number=data["sequenceNumber"],
            digest=data["digest"],
            network_total_transactions=data["networkTotalTransactions"],
            previous_digest=data.get("previousDigest"),
            epoch_rolling_gas_cost_summary=data.get("epochRollingGasCostSummary"),
            timestamp_ms=data.get("timestampMs", 0),
            transactions=[TransactionDigest.from_str(tx) for tx in data.get("transactions", [])],
            checkpoint_commitments=data.get("checkpointCommitments", []),
            validator_signature=data.get("validatorSignature")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Checkpoint to dictionary format."""
        result = {
            "epoch": self.epoch,
            "sequenceNumber": self.sequence_number,
            "digest": self.digest,
            "networkTotalTransactions": self.network_total_transactions,
            "timestampMs": self.timestamp_ms,
            "transactions": [str(tx) for tx in self.transactions],
            "checkpointCommitments": self.checkpoint_commitments,
        }
        
        if self.previous_digest:
            result["previousDigest"] = self.previous_digest
        if self.epoch_rolling_gas_cost_summary:
            result["epochRollingGasCostSummary"] = self.epoch_rolling_gas_cost_summary
        if self.validator_signature:
            result["validatorSignature"] = self.validator_signature
            
        return result


@dataclass
class CheckpointPage:
    """
    Represents a paginated response of checkpoints.
    """
    data: List[Checkpoint]
    next_cursor: Optional[str] = None
    has_next_page: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckpointPage":
        """Create a CheckpointPage from API response data."""
        return cls(
            data=[Checkpoint.from_dict(cp) for cp in data.get("data", [])],
            next_cursor=data.get("nextCursor"),
            has_next_page=data.get("hasNextPage", False)
        )


@dataclass
class ProtocolConfig:
    """
    Represents Sui protocol configuration.
    
    Corresponds to the ProtocolConfig schema in the Sui API.
    """
    version: int
    feature_flags: Dict[str, bool]
    max_tx_size_bytes: int
    max_input_objects: int
    max_size_written_objects: int
    max_size_written_objects_system_tx: int
    max_serialized_tx_effects_size_bytes: int
    max_serialized_tx_effects_size_bytes_system_tx: int
    max_gas_payment_objects: int
    max_modules_in_publish: int
    max_arguments: int
    max_type_arguments: int
    max_type_argument_depth: int
    max_pure_argument_size: int
    max_programmable_tx_commands: int
    move_binary_format_version: int
    min_move_binary_format_version: int
    max_move_object_size: int
    max_move_package_size: int
    max_tx_gas: int
    max_gas_price: int
    max_gas_computation_bucket: int
    gas_rounding_step: int
    max_loop_depth: int
    max_generic_instantiation_length: int
    max_function_parameters: int
    max_basic_blocks: int
    max_value_stack_size: int
    max_type_nodes: int
    max_push_size: int
    max_struct_definitions: int
    max_function_definitions: int
    max_fields_in_struct: int
    max_dependency_depth: int
    max_num_event_emit: int
    max_num_new_move_object_ids: int
    max_num_new_move_object_ids_system_tx: int
    max_num_deleted_move_object_ids: int
    max_num_deleted_move_object_ids_system_tx: int
    max_num_transferred_move_object_ids: int
    max_num_transferred_move_object_ids_system_tx: int
    max_event_emit_size: int
    max_event_emit_size_total: int
    max_bytes_written_per_transaction: int
    max_bytes_written_per_transaction_system_tx: int
    max_txn_expiry_ms: int
    max_num_input_objects: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProtocolConfig":
        """Create a ProtocolConfig from API response data."""
        # Helper function to get attribute value
        def get_attr_value(attr_name: str, default_value: int = 0) -> int:
            attr_data = data.get("attributes", {}).get(attr_name)
            if attr_data is None:
                return default_value
            # Attributes can be wrapped in type objects like {'u64': '1000'}
            if isinstance(attr_data, dict):
                for key, value in attr_data.items():
                    return int(value) if isinstance(value, str) else value
            return int(attr_data) if isinstance(attr_data, str) else attr_data
        
        return cls(
            version=int(data.get("protocolVersion", 0)),
            feature_flags=data.get("featureFlags", {}),
            max_tx_size_bytes=get_attr_value("max_tx_size_bytes"),
            max_input_objects=get_attr_value("max_input_objects"),
            max_size_written_objects=get_attr_value("max_size_written_objects"),
            max_size_written_objects_system_tx=get_attr_value("max_size_written_objects_system_tx"),
            max_serialized_tx_effects_size_bytes=get_attr_value("max_serialized_tx_effects_size_bytes"),
            max_serialized_tx_effects_size_bytes_system_tx=get_attr_value("max_serialized_tx_effects_size_bytes_system_tx"),
            max_gas_payment_objects=get_attr_value("max_gas_payment_objects"),
            max_modules_in_publish=get_attr_value("max_modules_in_publish"),
            max_arguments=get_attr_value("max_arguments"),
            max_type_arguments=get_attr_value("max_type_arguments"),
            max_type_argument_depth=get_attr_value("max_type_argument_depth"),
            max_pure_argument_size=get_attr_value("max_pure_argument_size"),
            max_programmable_tx_commands=get_attr_value("max_programmable_tx_commands"),
            move_binary_format_version=get_attr_value("move_binary_format_version"),
            min_move_binary_format_version=get_attr_value("min_move_binary_format_version"),
            max_move_object_size=get_attr_value("max_move_object_size"),
            max_move_package_size=get_attr_value("max_move_package_size"),
            max_tx_gas=get_attr_value("max_tx_gas"),
            max_gas_price=get_attr_value("max_gas_price"),
            max_gas_computation_bucket=get_attr_value("max_gas_computation_bucket"),
            gas_rounding_step=get_attr_value("gas_rounding_step"),
            max_loop_depth=get_attr_value("max_loop_depth"),
            max_generic_instantiation_length=get_attr_value("max_generic_instantiation_length"),
            max_function_parameters=get_attr_value("max_function_parameters"),
            max_basic_blocks=get_attr_value("max_basic_blocks"),
            max_value_stack_size=get_attr_value("max_value_stack_size"),
            max_type_nodes=get_attr_value("max_type_nodes"),
            max_push_size=get_attr_value("max_push_size"),
            max_struct_definitions=get_attr_value("max_struct_definitions"),
            max_function_definitions=get_attr_value("max_function_definitions"),
            max_fields_in_struct=get_attr_value("max_fields_in_struct"),
            max_dependency_depth=get_attr_value("max_dependency_depth"),
            max_num_event_emit=get_attr_value("max_num_event_emit"),
            max_num_new_move_object_ids=get_attr_value("max_num_new_move_object_ids"),
            max_num_new_move_object_ids_system_tx=get_attr_value("max_num_new_move_object_ids_system_tx"),
            max_num_deleted_move_object_ids=get_attr_value("max_num_deleted_move_object_ids"),
            max_num_deleted_move_object_ids_system_tx=get_attr_value("max_num_deleted_move_object_ids_system_tx"),
            max_num_transferred_move_object_ids=get_attr_value("max_num_transferred_move_object_ids"),
            max_num_transferred_move_object_ids_system_tx=get_attr_value("max_num_transferred_move_object_ids_system_tx"),
            max_event_emit_size=get_attr_value("max_event_emit_size"),
            max_event_emit_size_total=get_attr_value("max_event_emit_size_total"),
            max_bytes_written_per_transaction=get_attr_value("max_bytes_written_per_transaction"),
            max_bytes_written_per_transaction_system_tx=get_attr_value("max_bytes_written_per_transaction_system_tx"),
            max_txn_expiry_ms=get_attr_value("max_txn_expiry_ms"),
            max_num_input_objects=get_attr_value("max_num_input_objects"),
        )
