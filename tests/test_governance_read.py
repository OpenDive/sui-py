"""
Tests for the Governance Read API client.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from sui_py.client.governance_read_api import GovernanceReadClient
from sui_py.client.rest_client import RestClient
from sui_py.types import (
    CommitteeInfo, SuiSystemStateSummary, ValidatorApys, ValidatorApy, 
    DelegatedStake, SuiAddress, ObjectID
)
from sui_py.exceptions import SuiValidationError


@pytest.fixture
def mock_rest_client():
    """Create a mock REST client."""
    return AsyncMock(spec=RestClient)


@pytest.fixture
def governance_client(mock_rest_client):
    """Create a governance read client with mocked REST client."""
    return GovernanceReadClient(mock_rest_client)


class TestGovernanceReadClient:
    """Test suite for GovernanceReadClient."""
    
    @pytest.mark.asyncio
    async def test_get_reference_gas_price(self, governance_client, mock_rest_client):
        """Test getting reference gas price."""
        # Mock response
        mock_rest_client.call.return_value = "1000"
        
        # Call method
        result = await governance_client.get_reference_gas_price()
        
        # Assertions
        assert result == "1000"
        mock_rest_client.call.assert_called_once_with("suix_getReferenceGasPrice", [])
    
    @pytest.mark.asyncio
    async def test_get_committee_info_without_epoch(self, governance_client, mock_rest_client):
        """Test getting committee info without specifying epoch."""
        # Mock response
        mock_response = {
            "epoch": "750",
            "validators": [["pubkey1", "stake1"], ["pubkey2", "stake2"]]
        }
        mock_rest_client.call.return_value = mock_response
        
        # Call method
        result = await governance_client.get_committee_info()
        
        # Assertions
        assert isinstance(result, CommitteeInfo)
        assert result.epoch == "750"
        assert len(result.validators) == 2
        mock_rest_client.call.assert_called_once_with("suix_getCommitteeInfo", [])
    
    @pytest.mark.asyncio
    async def test_get_committee_info_with_epoch(self, governance_client, mock_rest_client):
        """Test getting committee info with specific epoch."""
        # Mock response
        mock_response = {
            "epoch": "749",
            "validators": [["pubkey1", "stake1"]]
        }
        mock_rest_client.call.return_value = mock_response
        
        # Call method
        result = await governance_client.get_committee_info("749")
        
        # Assertions
        assert isinstance(result, CommitteeInfo)
        assert result.epoch == "749"
        mock_rest_client.call.assert_called_once_with("suix_getCommitteeInfo", ["749"])
    
    @pytest.mark.asyncio
    async def test_get_latest_sui_system_state(self, governance_client, mock_rest_client):
        """Test getting latest system state."""
        # Mock response
        mock_response = {
            "epoch": "750",
            "protocolVersion": "84",
            "systemStateVersion": "1",
            "stakingPoolMappingsId": "0x123",
            "stakingPoolMappingsSize": "100",
            "inactivePoolsId": "0x456",
            "inactivePoolsSize": "10",
            "validatorCandidatesId": "0x789",
            "validatorCandidatesSize": "5",
            "pendingActiveValidatorsId": "0xabc",
            "pendingActiveValidatorsSize": "2",
            "pendingRemovals": ["1", "2"],
            "activeValidators": [
                {
                    "suiAddress": "0x123",
                    "protocolPubkeyBytes": "pubkey",
                    "networkPubkeyBytes": "netkey",
                    "workerPubkeyBytes": "workkey",
                    "proofOfPossessionBytes": "proof",
                    "name": "Test Validator",
                    "description": "A test validator",
                    "imageUrl": "http://image.url",
                    "projectUrl": "http://project.url",
                    "netAddress": "127.0.0.1:8080",
                    "p2pAddress": "127.0.0.1:8081",
                    "primaryAddress": "127.0.0.1:8082",
                    "workerAddress": "127.0.0.1:8083",
                    "votingPower": "1000",
                    "operationCapId": "0xop123",
                    "gasPrice": "1000",
                    "commissionRate": "500",
                    "nextEpochStake": "1000000",
                    "nextEpochGasPrice": "1000",
                    "nextEpochCommissionRate": "500",
                    "stakingPoolId": "0xpool123",
                    "stakingPoolSuiBalance": "1000000",
                    "rewardsPool": "50000",
                    "poolTokenBalance": "1000000",
                    "pendingStake": "0",
                    "pendingTotalSuiWithdraw": "0",
                    "pendingPoolTokenWithdraw": "0",
                    "exchangeRatesId": "0xrates123",
                    "exchangeRatesSize": "100"
                }
            ],
            "atRiskValidators": [],
            "validatorReportRecords": [],
            "totalStake": "1000000000",
            "storageFundTotalObjectStorageRebates": "100000",
            "storageFundNonRefundableBalance": "50000",
            "referenceGasPrice": "1000",
            "safeMode": False,
            "safeModeStorageRewards": "0",
            "safeModeComputationRewards": "0",
            "safeModeStorageRebates": "0",
            "safeModeNonRefundableStorageFee": "0",
            "epochStartTimestampMs": "1640995200000",
            "epochDurationMs": "86400000",
            "stakeSubsidyStartEpoch": "0",
            "maxValidatorCount": "150",
            "minValidatorJoiningStake": "30000000000",
            "validatorLowStakeThreshold": "20000000000",
            "validatorVeryLowStakeThreshold": "15000000000",
            "validatorLowStakeGracePeriod": "7",
            "stakeSubsidyBalance": "1000000000",
            "stakeSubsidyDistributionCounter": "100",
            "stakeSubsidyCurrentDistributionAmount": "10000000",
            "stakeSubsidyPeriodLength": "30",
            "stakeSubsidyDecreaseRate": 1000
        }
        mock_rest_client.call.return_value = mock_response
        
        # Call method
        result = await governance_client.get_latest_sui_system_state()
        
        # Assertions
        assert isinstance(result, SuiSystemStateSummary)
        assert result.epoch == "750"
        assert result.protocol_version == "84"
        assert len(result.active_validators) == 1
        assert result.active_validators[0].name == "Test Validator"
        assert result.safe_mode is False
        mock_rest_client.call.assert_called_once_with("suix_getLatestSuiSystemState", [])
    
    @pytest.mark.asyncio
    async def test_get_validators_apy(self, governance_client, mock_rest_client):
        """Test getting validator APY information."""
        # Mock response with valid 64-character hex addresses
        mock_response = {
            "epoch": "750",
            "apys": [
                {"address": "0x1234567890123456789012345678901234567890123456789012345678901234", "apy": 5.5},
                {"address": "0x4567890123456789012345678901234567890123456789012345678901234567", "apy": 4.2}
            ]
        }
        mock_rest_client.call.return_value = mock_response
        
        # Call method
        result = await governance_client.get_validators_apy()
        
        # Assertions
        assert isinstance(result, ValidatorApys)
        assert result.epoch == "750"
        assert len(result.apys) == 2
        assert isinstance(result.apys[0], ValidatorApy)
        assert str(result.apys[0].address) == "0x1234567890123456789012345678901234567890123456789012345678901234"
        assert result.apys[0].apy == 5.5
        mock_rest_client.call.assert_called_once_with("suix_getValidatorsApy", [])
    
    @pytest.mark.asyncio
    async def test_get_stakes(self, governance_client, mock_rest_client):
        """Test getting stakes for an address."""
        # Mock response with valid 64-character hex IDs
        mock_response = [
            {
                "stakes": [
                    {
                        "stakedSuiId": "0x1234567890123456789012345678901234567890123456789012345678901234",
                        "stakeRequestEpoch": "745",
                        "stakeActiveEpoch": "746",
                        "principal": "1000000000",
                        "status": "Active"
                    }
                ],
                "stakingPool": "0xpool123",
                "validatorAddress": "0xvalidator123"
            }
        ]
        mock_rest_client.call.return_value = mock_response
        
        # Call method
        result = await governance_client.get_stakes("0x123")
        
        # Assertions
        assert len(result) == 1
        assert isinstance(result[0], DelegatedStake)
        assert len(result[0].stakes) == 1
        assert result[0].staking_pool == "0xpool123"
        assert result[0].validator_address == "0xvalidator123"
        mock_rest_client.call.assert_called_once_with("suix_getStakes", ["0x123"])
    
    @pytest.mark.asyncio
    async def test_get_stakes_by_ids(self, governance_client, mock_rest_client):
        """Test getting stakes by IDs."""
        # Mock response with valid 64-character hex IDs
        mock_response = [
            {
                "stakes": [
                    {
                        "stakedSuiId": "0x1234567890123456789012345678901234567890123456789012345678901234",
                        "stakeRequestEpoch": "745",
                        "stakeActiveEpoch": "746",
                        "principal": "1000000000",
                        "status": "Active"
                    }
                ],
                "stakingPool": "0xpool123",
                "validatorAddress": "0xvalidator123"
            }
        ]
        mock_rest_client.call.return_value = mock_response
        
        # Call method with valid object IDs
        stake_ids = [
            "0x1234567890123456789012345678901234567890123456789012345678901234", 
            ObjectID("0x4567890123456789012345678901234567890123456789012345678901234567")
        ]
        result = await governance_client.get_stakes_by_ids(stake_ids)
        
        # Assertions
        assert len(result) == 1
        assert isinstance(result[0], DelegatedStake)
        mock_rest_client.call.assert_called_once_with("suix_getStakesByIds", [
            ["0x1234567890123456789012345678901234567890123456789012345678901234", 
             "0x4567890123456789012345678901234567890123456789012345678901234567"]
        ])
    
    def test_validate_address_string(self, governance_client):
        """Test address validation with string input."""
        valid_address = "0x123abc"
        result = governance_client._validate_address(valid_address)
        assert result == valid_address
    
    def test_validate_address_sui_address(self, governance_client):
        """Test address validation with SuiAddress input."""
        # Use a valid 64-character hex address
        sui_address = SuiAddress("0x1234567890123456789012345678901234567890123456789012345678901234")
        result = governance_client._validate_address(sui_address)
        assert result == str(sui_address)
    
    def test_validate_address_invalid_type(self, governance_client):
        """Test address validation with invalid type."""
        with pytest.raises(SuiValidationError, match="Address must be a string or SuiAddress"):
            governance_client._validate_address(123)
    
    def test_validate_address_invalid_format(self, governance_client):
        """Test address validation with invalid format."""
        with pytest.raises(SuiValidationError, match="Invalid Sui address format"):
            governance_client._validate_address("invalid_address")
    
    def test_validate_address_invalid_hex(self, governance_client):
        """Test address validation with invalid hex."""
        with pytest.raises(SuiValidationError, match="Invalid Sui address format"):
            governance_client._validate_address("0xzzzz") 