"""
Tests for Coin Query API schemas.

Tests the typed schemas for proper validation, parsing, and functionality.
"""

import pytest
from sui_py.types import (
    SuiAddress, ObjectID, TransactionDigest, 
    Balance, Coin, SuiCoinMetadata, Supply, Page
)
from sui_py.exceptions import SuiValidationError


class TestBaseTypes:
    """Test base type validation and functionality."""
    
    def test_sui_address_valid(self):
        """Test valid SuiAddress creation."""
        valid_address = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        address = SuiAddress.from_str(valid_address)
        assert str(address) == valid_address
        assert repr(address) == f"SuiAddress('{valid_address}')"
    
    def test_sui_address_invalid(self):
        """Test invalid SuiAddress validation."""
        with pytest.raises(SuiValidationError):
            SuiAddress.from_str("invalid")
        
        with pytest.raises(SuiValidationError):
            SuiAddress.from_str("0x123")  # Too short
        
        with pytest.raises(SuiValidationError):
            SuiAddress.from_str("1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")  # No 0x prefix
    
    def test_object_id_valid(self):
        """Test valid ObjectID creation."""
        valid_id = "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        obj_id = ObjectID.from_str(valid_id)
        assert str(obj_id) == valid_id
    
    def test_transaction_digest_valid(self):
        """Test valid TransactionDigest creation."""
        valid_digest = "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF"  # Example base58
        digest = TransactionDigest.from_str(valid_digest)
        assert str(digest) == valid_digest
    
    def test_transaction_digest_invalid(self):
        """Test invalid TransactionDigest validation."""
        with pytest.raises(SuiValidationError):
            TransactionDigest.from_str("short")  # Too short
        
        with pytest.raises(SuiValidationError):
            TransactionDigest.from_str("a" * 60)  # Too long


class TestCoinTypes:
    """Test coin-specific type functionality."""
    
    def test_balance_from_dict(self):
        """Test Balance creation from dictionary."""
        data = {
            "coinType": "0x2::sui::SUI",
            "coinObjectCount": 5,
            "totalBalance": "1000000000",
            "lockedBalance": {}
        }
        
        balance = Balance.from_dict(data)
        assert balance.coin_type == "0x2::sui::SUI"
        assert balance.coin_object_count == 5
        assert balance.total_balance == "1000000000"
        assert balance.total_balance_int == 1000000000
        assert not balance.is_zero()
    
    def test_balance_zero(self):
        """Test Balance zero detection."""
        data = {
            "coinType": "0x2::sui::SUI",
            "coinObjectCount": 0,
            "totalBalance": "0",
            "lockedBalance": {}
        }
        
        balance = Balance.from_dict(data)
        assert balance.is_zero()
    
    def test_coin_from_dict(self):
        """Test Coin creation from dictionary."""
        data = {
            "coinType": "0x2::sui::SUI",
            "coinObjectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "version": "123",
            "digest": "abc123",
            "balance": "500000000",
            "previousTransaction": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF"
        }
        
        coin = Coin.from_dict(data)
        assert coin.coin_type == "0x2::sui::SUI"
        assert isinstance(coin.coin_object_id, ObjectID)
        assert str(coin.coin_object_id) == data["coinObjectId"]
        assert coin.balance_int == 500000000
        assert not coin.is_zero()
    
    def test_sui_coin_metadata_from_dict(self):
        """Test SuiCoinMetadata creation from dictionary."""
        data = {
            "decimals": 9,
            "name": "Sui",
            "symbol": "SUI",
            "description": "The native token of Sui",
            "iconUrl": "https://example.com/sui.png",
            "id": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        }
        
        metadata = SuiCoinMetadata.from_dict(data)
        assert metadata.decimals == 9
        assert metadata.name == "Sui"
        assert metadata.symbol == "SUI"
        assert metadata.icon_url == "https://example.com/sui.png"
        assert isinstance(metadata.id, ObjectID)
    
    def test_sui_coin_metadata_formatting(self):
        """Test SuiCoinMetadata amount formatting."""
        data = {
            "decimals": 9,
            "name": "Sui",
            "symbol": "SUI",
            "description": "The native token of Sui"
        }
        
        metadata = SuiCoinMetadata.from_dict(data)
        
        # Test formatting
        amount = 1000000000  # 1 SUI in MIST
        formatted = metadata.format_amount(amount)
        assert formatted == 1.0
        
        # Test parsing
        parsed = metadata.parse_amount(1.5)
        assert parsed == 1500000000
    
    def test_supply_from_dict(self):
        """Test Supply creation from dictionary."""
        data = {"value": "10000000000000000000"}
        
        supply = Supply.from_dict(data)
        assert supply.value == "10000000000000000000"
        assert supply.value_int == 10000000000000000000
    
    def test_supply_format_with_metadata(self):
        """Test Supply formatting with metadata."""
        supply_data = {"value": "10000000000000000000"}
        metadata_data = {
            "decimals": 9,
            "name": "Sui",
            "symbol": "SUI",
            "description": "The native token of Sui"
        }
        
        supply = Supply.from_dict(supply_data)
        metadata = SuiCoinMetadata.from_dict(metadata_data)
        
        formatted = supply.format_with_metadata(metadata)
        assert formatted == 10000000000.0


class TestPagination:
    """Test pagination functionality."""
    
    def test_page_from_dict_simple(self):
        """Test Page creation from dictionary."""
        data = {
            "data": ["item1", "item2", "item3"],
            "hasNextPage": True,
            "nextCursor": "cursor123"
        }
        
        page = Page.from_dict(data)
        assert len(page) == 3
        assert page.has_next_page
        assert page.next_cursor == "cursor123"
        assert list(page) == ["item1", "item2", "item3"]
        assert page[0] == "item1"
    
    def test_page_from_dict_with_parser(self):
        """Test Page creation with item parser."""
        balance_data = [
            {
                "coinType": "0x2::sui::SUI",
                "coinObjectCount": 5,
                "totalBalance": "1000000000",
                "lockedBalance": {}
            }
        ]
        
        data = {
            "data": balance_data,
            "hasNextPage": False
        }
        
        page = Page.from_dict(data, Balance.from_dict)
        assert len(page) == 1
        assert isinstance(page[0], Balance)
        assert page[0].coin_type == "0x2::sui::SUI"
        assert not page.has_next_page
        assert page.next_cursor is None
    
    def test_page_empty(self):
        """Test empty page."""
        data = {
            "data": [],
            "hasNextPage": False
        }
        
        page = Page.from_dict(data)
        assert len(page) == 0
        assert page.is_empty()
        assert not page.has_next_page


class TestTypeConversions:
    """Test type conversion and serialization."""
    
    def test_balance_round_trip(self):
        """Test Balance dictionary round trip."""
        original_data = {
            "coinType": "0x2::sui::SUI",
            "coinObjectCount": 5,
            "totalBalance": "1000000000",
            "lockedBalance": {"test": "value"}
        }
        
        balance = Balance.from_dict(original_data)
        converted_data = balance.to_dict()
        
        assert converted_data == original_data
    
    def test_coin_round_trip(self):
        """Test Coin dictionary round trip."""
        original_data = {
            "coinType": "0x2::sui::SUI",
            "coinObjectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "version": "123",
            "digest": "abc123",
            "balance": "500000000",
            "previousTransaction": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF"
        }
        
        coin = Coin.from_dict(original_data)
        converted_data = coin.to_dict()
        
        assert converted_data == original_data
    
    def test_metadata_round_trip(self):
        """Test SuiCoinMetadata dictionary round trip."""
        original_data = {
            "decimals": 9,
            "name": "Sui",
            "symbol": "SUI",
            "description": "The native token of Sui",
            "iconUrl": "https://example.com/sui.png",
            "id": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        }
        
        metadata = SuiCoinMetadata.from_dict(original_data)
        converted_data = metadata.to_dict()
        
        assert converted_data == original_data 