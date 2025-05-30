"""
Governance-related type definitions for Sui blockchain.

This module contains types related to validator governance, staking,
and system state management according to the Sui JSON-RPC API schemas.
"""

from typing import List, Optional, Union
from dataclasses import dataclass, field
from decimal import Decimal

from .base import SuiAddress, ObjectID


@dataclass(frozen=True)
class CommitteeInfo:
    """
    RPC representation of the Committee type.
    
    Attributes:
        epoch: The current epoch number as a string
        validators: List of validator public key and stake pairs
    """
    epoch: str
    validators: List[List[str]]


@dataclass(frozen=True)
class DelegatedStake:
    """
    Represents delegated stake information.
    
    Attributes:
        stakes: List of stake objects
        staking_pool: Staking pool object ID
        validator_address: Validator's address
    """
    stakes: List['StakeObject']
    staking_pool: str
    validator_address: str


@dataclass(frozen=True)
class StakeObject:
    """
    Individual stake object information.
    
    Attributes:
        staked_sui_id: ID of the staked SUI object
        stake_request_epoch: Epoch when stake was requested
        stake_active_epoch: Epoch when stake became active
        principal: Principal amount staked
        status: Current status of the stake
    """
    staked_sui_id: ObjectID
    stake_request_epoch: str
    stake_active_epoch: str
    principal: str
    status: str


@dataclass(frozen=True)
class ValidatorApy:
    """
    Validator APY information.
    
    Attributes:
        address: Validator's Sui address
        apy: Annual percentage yield as a number
    """
    address: SuiAddress
    apy: float


@dataclass(frozen=True)
class ValidatorApys:
    """
    Collection of validator APY information for an epoch.
    
    Attributes:
        apys: List of validator APY records
        epoch: The epoch number
    """
    apys: List[ValidatorApy]
    epoch: str


@dataclass(frozen=True)
class SuiValidatorSummary:
    """
    JSON-RPC type for the SUI validator summary.
    
    This flattens all inner structures to top-level fields so that they are
    decoupled from the internal definitions.
    """
    sui_address: str
    protocol_pubkey_bytes: str
    network_pubkey_bytes: str
    worker_pubkey_bytes: str
    proof_of_possession_bytes: str
    name: str
    description: str
    image_url: str
    project_url: str
    net_address: str
    p2p_address: str
    primary_address: str
    worker_address: str
    next_epoch_protocol_pubkey_bytes: Optional[str]
    next_epoch_proof_of_possession: Optional[str]
    next_epoch_network_pubkey_bytes: Optional[str]
    next_epoch_worker_pubkey_bytes: Optional[str]
    next_epoch_net_address: Optional[str]
    next_epoch_p2p_address: Optional[str]
    next_epoch_primary_address: Optional[str]
    next_epoch_worker_address: Optional[str]
    voting_power: str
    operation_cap_id: str
    gas_price: str
    commission_rate: str
    next_epoch_stake: str
    next_epoch_gas_price: str
    next_epoch_commission_rate: str
    staking_pool_id: str
    staking_pool_activation_epoch: Optional[str]
    staking_pool_deactivation_epoch: Optional[str]
    staking_pool_sui_balance: str
    rewards_pool: str
    pool_token_balance: str
    pending_stake: str
    pending_total_sui_withdraw: str
    pending_pool_token_withdraw: str
    exchange_rates_id: str
    exchange_rates_size: str


@dataclass(frozen=True)
class SuiSystemStateSummary:
    """
    JSON-RPC type for the SUI system state object.
    
    This flattens all fields to make them top-level fields such that it has
    minimum dependencies to the internal data structures of the SUI system state type.
    """
    epoch: str
    protocol_version: str
    system_state_version: str
    staking_pool_mappings_id: str
    staking_pool_mappings_size: str
    inactive_pools_id: str
    inactive_pools_size: str
    validator_candidates_id: str
    validator_candidates_size: str
    pending_active_validators_id: str
    pending_active_validators_size: str
    pending_removals: List[str]
    active_validators: List[SuiValidatorSummary]
    at_risk_validators: List[List[str]]
    validator_report_records: List[List[Union[str, List[str]]]]
    total_stake: str
    reward_slashing_rate: str
    storage_fund_total_object_storage_rebates: str
    storage_fund_non_refundable_balance: str
    reference_gas_price: str
    safe_mode: bool
    safe_mode_storage_rewards: str
    safe_mode_computation_rewards: str
    safe_mode_storage_rebates: str
    safe_mode_non_refundable_storage_fee: str
    epoch_start_timestamp_ms: str
    epoch_duration_ms: str
    stake_subsidy_start_epoch: str
    max_validator_count: str
    min_validator_joining_stake: str
    validator_low_stake_threshold: str
    validator_very_low_stake_threshold: str
    validator_low_stake_grace_period: str
    stake_subsidy_balance: str
    stake_subsidy_distribution_counter: str
    stake_subsidy_current_distribution_amount: str
    stake_subsidy_period_length: str
    stake_subsidy_decrease_rate: int


# Type aliases for convenience
Stake = DelegatedStake
ValidatorSummary = SuiValidatorSummary
SystemState = SuiSystemStateSummary 