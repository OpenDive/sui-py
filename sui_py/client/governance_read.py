"""
Governance Read API client for Sui blockchain.

Implements all governance-related read RPC methods from the Sui JSON-RPC API.
These methods provide access to validator information, system state, and staking data.
"""

from typing import Any, Dict, List, Optional, Union

from .rest_client import RestClient
from ..exceptions import SuiValidationError
from ..types import (
    CommitteeInfo, DelegatedStake, ValidatorApys, SuiSystemStateSummary, 
    SuiAddress, ObjectID, Page
)


class GovernanceReadClient:
    """
    Client for Sui Governance Read API operations.
    
    Provides methods for querying validator information, system state,
    staking data, and other governance-related information.
    All methods return typed objects corresponding to the Sui JSON-RPC API schemas.
    """
    
    def __init__(self, rest_client: RestClient):
        """
        Initialize the Governance Read client.
        
        Args:
            rest_client: The underlying REST client for making RPC calls
        """
        self.rest_client = rest_client
    
    @staticmethod
    def _validate_address(address: Union[str, SuiAddress]) -> str:
        """
        Validate and normalize a Sui address.
        
        Args:
            address: The address string or SuiAddress to validate
            
        Returns:
            The normalized address string
            
        Raises:
            SuiValidationError: If the address format is invalid
        """
        if isinstance(address, SuiAddress):
            return str(address)
        
        if not isinstance(address, str):
            raise SuiValidationError("Address must be a string or SuiAddress")
        
        # Basic validation for Sui address format (0x prefix and hex)
        if not address.startswith('0x') or len(address) < 3:
            raise SuiValidationError("Invalid Sui address format")
        
        try:
            # Check if the hex part is valid
            int(address[2:], 16)
        except ValueError:
            raise SuiValidationError("Invalid Sui address format")
        
        return address

    async def get_committee_info(self, epoch: Optional[str] = None) -> CommitteeInfo:
        """
        Return the committee information for the asked epoch.
        
        Args:
            epoch: The epoch to get committee info for. If None, returns current epoch.
            
        Returns:
            CommitteeInfo object containing epoch and validator information
            
        Raises:
            SuiRpcError: If the RPC call fails
        """
        params = []
        if epoch is not None:
            params.append(epoch)
        
        response = await self.rest_client.call("suix_getCommitteeInfo", params)
        
        return CommitteeInfo(
            epoch=response["epoch"],
            validators=response["validators"]
        )

    async def get_latest_sui_system_state(self) -> SuiSystemStateSummary:
        """
        Return the latest Sui system state.
        
        Returns:
            SuiSystemStateSummary object containing comprehensive system state information
            
        Raises:
            SuiRpcError: If the RPC call fails
        """
        response = await self.rest_client.call("suix_getLatestSuiSystemState", [])
        
        return SuiSystemStateSummary(
            epoch=response["epoch"],
            protocol_version=response["protocolVersion"],
            system_state_version=response["systemStateVersion"],
            staking_pool_mappings_id=response["stakingPoolMappingsId"],
            staking_pool_mappings_size=response["stakingPoolMappingsSize"],
            inactive_pools_id=response["inactivePoolsId"],
            inactive_pools_size=response["inactivePoolsSize"],
            validator_candidates_id=response["validatorCandidatesId"],
            validator_candidates_size=response["validatorCandidatesSize"],
            pending_active_validators_id=response["pendingActiveValidatorsId"],
            pending_active_validators_size=response["pendingActiveValidatorsSize"],
            pending_removals=response["pendingRemovals"],
            active_validators=[
                self._parse_validator_summary(v) for v in response["activeValidators"]
            ],
            at_risk_validators=response["atRiskValidators"],
            validator_report_records=response["validatorReportRecords"],
            total_stake=response["totalStake"],
            reward_slashing_rate=response.get("rewardSlashingRate", "0"),
            storage_fund_total_object_storage_rebates=response["storageFundTotalObjectStorageRebates"],
            storage_fund_non_refundable_balance=response["storageFundNonRefundableBalance"],
            reference_gas_price=response["referenceGasPrice"],
            safe_mode=response["safeMode"],
            safe_mode_storage_rewards=response["safeModeStorageRewards"],
            safe_mode_computation_rewards=response["safeModeComputationRewards"],
            safe_mode_storage_rebates=response["safeModeStorageRebates"],
            safe_mode_non_refundable_storage_fee=response["safeModeNonRefundableStorageFee"],
            epoch_start_timestamp_ms=response["epochStartTimestampMs"],
            epoch_duration_ms=response["epochDurationMs"],
            stake_subsidy_start_epoch=response["stakeSubsidyStartEpoch"],
            max_validator_count=response["maxValidatorCount"],
            min_validator_joining_stake=response["minValidatorJoiningStake"],
            validator_low_stake_threshold=response["validatorLowStakeThreshold"],
            validator_very_low_stake_threshold=response["validatorVeryLowStakeThreshold"],
            validator_low_stake_grace_period=response["validatorLowStakeGracePeriod"],
            stake_subsidy_balance=response["stakeSubsidyBalance"],
            stake_subsidy_distribution_counter=response["stakeSubsidyDistributionCounter"],
            stake_subsidy_current_distribution_amount=response["stakeSubsidyCurrentDistributionAmount"],
            stake_subsidy_period_length=response["stakeSubsidyPeriodLength"],
            stake_subsidy_decrease_rate=response["stakeSubsidyDecreaseRate"]
        )

    async def get_reference_gas_price(self) -> str:
        """
        Return the reference gas price for the network.
        
        Returns:
            The reference gas price as a string
            
        Raises:
            SuiRpcError: If the RPC call fails
        """
        response = await self.rest_client.call("suix_getReferenceGasPrice", [])
        return str(response)

    async def get_stakes(self, owner: Union[str, SuiAddress]) -> List[DelegatedStake]:
        """
        Return all [DelegatedStake] owned by an address.
        
        Args:
            owner: The owner address to query stakes for
            
        Returns:
            List of DelegatedStake objects
            
        Raises:
            SuiValidationError: If the address format is invalid
            SuiRpcError: If the RPC call fails
        """
        owner_addr = self._validate_address(owner)
        response = await self.rest_client.call("suix_getStakes", [owner_addr])
        
        stakes = []
        for stake_data in response:
            stakes.append(DelegatedStake(
                stakes=[self._parse_stake_object(s) for s in stake_data["stakes"]],
                staking_pool=stake_data["stakingPool"],
                validator_address=stake_data["validatorAddress"]
            ))
        
        return stakes

    async def get_stakes_by_ids(self, staked_sui_ids: List[Union[str, ObjectID]]) -> List[DelegatedStake]:
        """
        Return all [DelegatedStake] specified by staked SUI IDs.
        
        Args:
            staked_sui_ids: List of staked SUI object IDs to query
            
        Returns:
            List of DelegatedStake objects
            
        Raises:
            SuiRpcError: If the RPC call fails
        """
        # Convert ObjectID objects to strings if needed
        ids = [str(obj_id) for obj_id in staked_sui_ids]
        
        response = await self.rest_client.call("suix_getStakesByIds", [ids])
        
        stakes = []
        for stake_data in response:
            stakes.append(DelegatedStake(
                stakes=[self._parse_stake_object(s) for s in stake_data["stakes"]],
                staking_pool=stake_data["stakingPool"],
                validator_address=stake_data["validatorAddress"]
            ))
        
        return stakes

    async def get_validators_apy(self) -> ValidatorApys:
        """
        Return the validator APY for the current epoch.
        
        Returns:
            ValidatorApys object containing APY information for all validators
            
        Raises:
            SuiRpcError: If the RPC call fails
        """
        response = await self.rest_client.call("suix_getValidatorsApy", [])
        
        from ..types.governance import ValidatorApy
        
        apys = []
        for apy_data in response["apys"]:
            apys.append(ValidatorApy(
                address=SuiAddress(apy_data["address"]),
                apy=float(apy_data["apy"])
            ))
        
        return ValidatorApys(
            apys=apys,
            epoch=response["epoch"]
        )

    def _parse_validator_summary(self, data: Dict[str, Any]) -> 'SuiValidatorSummary':
        """
        Parse validator summary data from JSON response.
        
        Args:
            data: Raw validator data from JSON-RPC response
            
        Returns:
            SuiValidatorSummary object
        """
        from ..types.governance import SuiValidatorSummary
        
        return SuiValidatorSummary(
            sui_address=data["suiAddress"],
            protocol_pubkey_bytes=data["protocolPubkeyBytes"],
            network_pubkey_bytes=data["networkPubkeyBytes"],
            worker_pubkey_bytes=data["workerPubkeyBytes"],
            proof_of_possession_bytes=data["proofOfPossessionBytes"],
            name=data["name"],
            description=data["description"],
            image_url=data["imageUrl"],
            project_url=data["projectUrl"],
            net_address=data["netAddress"],
            p2p_address=data["p2pAddress"],
            primary_address=data["primaryAddress"],
            worker_address=data["workerAddress"],
            next_epoch_protocol_pubkey_bytes=data.get("nextEpochProtocolPubkeyBytes"),
            next_epoch_proof_of_possession=data.get("nextEpochProofOfPossession"),
            next_epoch_network_pubkey_bytes=data.get("nextEpochNetworkPubkeyBytes"),
            next_epoch_worker_pubkey_bytes=data.get("nextEpochWorkerPubkeyBytes"),
            next_epoch_net_address=data.get("nextEpochNetAddress"),
            next_epoch_p2p_address=data.get("nextEpochP2pAddress"),
            next_epoch_primary_address=data.get("nextEpochPrimaryAddress"),
            next_epoch_worker_address=data.get("nextEpochWorkerAddress"),
            voting_power=data["votingPower"],
            operation_cap_id=data["operationCapId"],
            gas_price=data["gasPrice"],
            commission_rate=data["commissionRate"],
            next_epoch_stake=data["nextEpochStake"],
            next_epoch_gas_price=data["nextEpochGasPrice"],
            next_epoch_commission_rate=data["nextEpochCommissionRate"],
            staking_pool_id=data["stakingPoolId"],
            staking_pool_activation_epoch=data.get("stakingPoolActivationEpoch"),
            staking_pool_deactivation_epoch=data.get("stakingPoolDeactivationEpoch"),
            staking_pool_sui_balance=data["stakingPoolSuiBalance"],
            rewards_pool=data["rewardsPool"],
            pool_token_balance=data["poolTokenBalance"],
            pending_stake=data["pendingStake"],
            pending_total_sui_withdraw=data["pendingTotalSuiWithdraw"],
            pending_pool_token_withdraw=data["pendingPoolTokenWithdraw"],
            exchange_rates_id=data["exchangeRatesId"],
            exchange_rates_size=data["exchangeRatesSize"]
        )

    def _parse_stake_object(self, data: Dict[str, Any]) -> 'StakeObject':
        """
        Parse stake object data from JSON response.
        
        Args:
            data: Raw stake object data from JSON-RPC response
            
        Returns:
            StakeObject
        """
        from ..types.governance import StakeObject
        
        return StakeObject(
            staked_sui_id=ObjectID(data["stakedSuiId"]),
            stake_request_epoch=data["stakeRequestEpoch"],
            stake_active_epoch=data["stakeActiveEpoch"],
            principal=data["principal"],
            status=data["status"]
        ) 