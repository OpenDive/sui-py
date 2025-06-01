"""
Tests for Extended API schemas.

Tests the typed schemas for proper validation, parsing, and functionality.
"""

import pytest
from sui_py.types import (
    # Base types
    SuiAddress, ObjectID, TransactionDigest, Base64,
    # Extended types
    DynamicFieldName, DynamicFieldInfo, ObjectOwner, SuiObjectData, SuiObjectResponse,
    SuiEvent, SuiTransactionBlock, SuiTransactionBlockResponse,
    EventFilter, TransactionFilter, Page
)
from sui_py.exceptions import SuiValidationError


class TestDynamicFields:
    """Test dynamic field types."""
    
    def test_dynamic_field_name_from_dict(self):
        """Test DynamicFieldName creation from dictionary."""
        data = {
            "type": "0x1::string::String",
            "value": "test_field"
        }
        
        field_name = DynamicFieldName.from_dict(data)
        assert field_name.type == "0x1::string::String"
        assert field_name.value == "test_field"
    
    def test_dynamic_field_name_round_trip(self):
        """Test DynamicFieldName dictionary round trip."""
        original_data = {
            "type": "u64",
            "value": 42
        }
        
        field_name = DynamicFieldName.from_dict(original_data)
        converted_data = field_name.to_dict()
        
        assert converted_data == original_data
    
    def test_dynamic_field_info_from_dict(self):
        """Test DynamicFieldInfo creation from dictionary."""
        data = {
            "name": {
                "type": "0x1::string::String",
                "value": "test_field"
            },
            "bcsName": "0x746573745f6669656c64",
            "type": "DynamicField",
            "objectType": "0x2::dynamic_field::Field<0x1::string::String, u64>",
            "objectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "version": 1,
            "digest": "abc123"
        }
        
        field_info = DynamicFieldInfo.from_dict(data)
        assert isinstance(field_info.name, DynamicFieldName)
        assert field_info.name.type == "0x1::string::String"
        assert field_info.bcs_name == "0x746573745f6669656c64"
        assert field_info.type == "DynamicField"
        assert isinstance(field_info.object_id, ObjectID)
        assert field_info.version == 1


class TestObjectTypes:
    """Test object-related types."""
    
    def test_object_owner_address_owner(self):
        """Test ObjectOwner with AddressOwner."""
        data = {
            "AddressOwner": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        }
        
        owner = ObjectOwner.from_dict(data)
        assert owner.owner_type == "AddressOwner"
        assert isinstance(owner.address, SuiAddress)
        assert str(owner.address) == data["AddressOwner"]
    
    def test_object_owner_object_owner(self):
        """Test ObjectOwner with ObjectOwner."""
        data = {
            "ObjectOwner": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        }
        
        owner = ObjectOwner.from_dict(data)
        assert owner.owner_type == "ObjectOwner"
        assert isinstance(owner.object_id, ObjectID)
        assert str(owner.object_id) == data["ObjectOwner"]
    
    def test_object_owner_shared(self):
        """Test ObjectOwner with Shared."""
        data = {
            "Shared": {
                "initial_shared_version": 123
            }
        }
        
        owner = ObjectOwner.from_dict(data)
        assert owner.owner_type == "Shared"
        assert owner.initial_shared_version == 123
    
    def test_object_owner_immutable(self):
        """Test ObjectOwner with Immutable."""
        data = "Immutable"
        
        owner = ObjectOwner.from_dict(data)
        assert owner.owner_type == "Immutable"
    
    def test_sui_object_data_from_dict(self):
        """Test SuiObjectData creation from dictionary."""
        data = {
            "objectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "version": 1,
            "digest": "abc123",
            "type": "0x2::coin::Coin<0x2::sui::SUI>",
            "owner": {
                "AddressOwner": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
            },
            "previousTransaction": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
            "storageRebate": 100,
            "content": {
                "dataType": "moveObject",
                "type": "0x2::coin::Coin<0x2::sui::SUI>",
                "hasPublicTransfer": True,
                "fields": {
                    "balance": "1000000000",
                    "id": {
                        "id": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
                    }
                }
            }
        }
        
        obj_data = SuiObjectData.from_dict(data)
        assert isinstance(obj_data.object_id, ObjectID)
        assert obj_data.version == 1
        assert obj_data.type == "0x2::coin::Coin<0x2::sui::SUI>"
        assert isinstance(obj_data.owner, ObjectOwner)
        assert obj_data.owner.owner_type == "AddressOwner"
        assert isinstance(obj_data.previous_transaction, TransactionDigest)
        assert obj_data.storage_rebate == 100
        assert obj_data.content is not None
    
    def test_sui_object_response_success(self):
        """Test SuiObjectResponse with successful data."""
        data = {
            "data": {
                "objectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "version": 1,
                "digest": "abc123"
            }
        }
        
        response = SuiObjectResponse.from_dict(data)
        assert response.is_success()
        assert isinstance(response.data, SuiObjectData)
        assert response.error is None
    
    def test_sui_object_response_error(self):
        """Test SuiObjectResponse with error."""
        data = {
            "error": {
                "code": "objectNotFound",
                "message": "Object not found"
            }
        }
        
        response = SuiObjectResponse.from_dict(data)
        assert not response.is_success()
        assert response.data is None
        assert response.error is not None


class TestEventTypes:
    """Test event-related types."""
    
    def test_sui_event_from_dict(self):
        """Test SuiEvent creation from dictionary."""
        data = {
            "id": {
                "txDigest": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
                "eventSeq": "0"
            },
            "packageId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "transactionModule": "coin",
            "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "type": "0x2::coin::CoinCreated<0x2::sui::SUI>",
            "parsedJson": {
                "amount": "1000000000",
                "owner": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
            },
            "timestampMs": 1234567890000
        }
        
        event = SuiEvent.from_dict(data)
        assert event.id == data["id"]
        assert isinstance(event.package_id, ObjectID)
        assert event.transaction_module == "coin"
        assert isinstance(event.sender, SuiAddress)
        assert event.type == "0x2::coin::CoinCreated<0x2::sui::SUI>"
        assert event.parsed_json == data["parsedJson"]
        assert event.timestamp_ms == 1234567890000


class TestTransactionTypes:
    """Test transaction-related types."""
    
    def test_sui_transaction_block_from_dict(self):
        """Test SuiTransactionBlock creation from dictionary."""
        data = {
            "data": {
                "messageVersion": "v1",
                "transaction": {
                    "kind": "ProgrammableTransaction",
                    "inputs": [],
                    "transactions": []
                },
                "sender": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "gasData": {
                    "payment": [],
                    "owner": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                    "price": "1000",
                    "budget": "1000000"
                }
            },
            "txSignatures": ["signature1", "signature2"]
        }
        
        tx_block = SuiTransactionBlock.from_dict(data)
        assert tx_block.data == data["data"]
        assert tx_block.tx_signatures == ["signature1", "signature2"]
    
    def test_sui_transaction_block_response_from_dict(self):
        """Test SuiTransactionBlockResponse creation from dictionary."""
        data = {
            "digest": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
            "transaction": {
                "data": {
                    "messageVersion": "v1",
                    "transaction": {
                        "kind": "ProgrammableTransaction"
                    }
                },
                "txSignatures": ["sig1"]
            },
            "effects": {
                "messageVersion": "v1",
                "status": {"status": "success"},
                "executedEpoch": "0"
            },
            "events": [
                {
                    "id": {
                        "txDigest": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
                        "eventSeq": "0"
                    },
                    "packageId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                    "transactionModule": "test",
                    "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                    "type": "test::Event"
                }
            ],
            "timestampMs": 1234567890000,
            "checkpoint": 100
        }
        
        response = SuiTransactionBlockResponse.from_dict(data)
        assert isinstance(response.digest, TransactionDigest)
        assert isinstance(response.transaction, SuiTransactionBlock)
        assert response.effects is not None
        assert len(response.events) == 1
        assert isinstance(response.events[0], SuiEvent)
        assert response.timestamp_ms == 1234567890000
        assert response.checkpoint == 100


class TestQueryFilters:
    """Test query filter helper classes."""
    
    def test_event_filter_by_package(self):
        """Test EventFilter.by_package."""
        package_id = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        filter_dict = EventFilter.by_package(package_id)
        
        assert filter_dict == {"Package": package_id}
    
    def test_event_filter_by_module(self):
        """Test EventFilter.by_module."""
        package_id = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        module_name = "coin"
        filter_dict = EventFilter.by_module(package_id, module_name)
        
        expected = {
            "MoveEventModule": {
                "package": package_id,
                "module": module_name
            }
        }
        assert filter_dict == expected
    
    def test_event_filter_by_sender(self):
        """Test EventFilter.by_sender."""
        sender = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        filter_dict = EventFilter.by_sender(sender)
        
        assert filter_dict == {"Sender": sender}
    
    def test_event_filter_by_time_range(self):
        """Test EventFilter.by_time_range."""
        start_time = 1234567890000
        end_time = 1234567900000
        filter_dict = EventFilter.by_time_range(start_time, end_time)
        
        expected = {
            "TimeRange": {
                "start_time": start_time,
                "end_time": end_time
            }
        }
        assert filter_dict == expected
    
    def test_transaction_filter_by_checkpoint(self):
        """Test TransactionFilter.by_checkpoint."""
        checkpoint = 100
        filter_dict = TransactionFilter.by_checkpoint(checkpoint)
        
        assert filter_dict == {"Checkpoint": checkpoint}
    
    def test_transaction_filter_by_move_function(self):
        """Test TransactionFilter.by_move_function."""
        package_id = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        module = "coin"
        function = "transfer"
        filter_dict = TransactionFilter.by_move_function(package_id, module, function)
        
        expected = {
            "MoveFunction": {
                "package": package_id,
                "module": module,
                "function": function
            }
        }
        assert filter_dict == expected
    
    def test_transaction_filter_by_from_address(self):
        """Test TransactionFilter.by_from_address."""
        address = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        filter_dict = TransactionFilter.by_from_address(address)
        
        assert filter_dict == {"FromAddress": address}


class TestTypeConversions:
    """Test type conversion and serialization."""
    
    def test_dynamic_field_info_round_trip(self):
        """Test DynamicFieldInfo dictionary round trip."""
        original_data = {
            "name": {
                "type": "u64",
                "value": 42
            },
            "bcsName": "0x2a",
            "type": "DynamicField",
            "objectType": "0x2::dynamic_field::Field<u64, 0x1::string::String>",
            "objectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "version": 1,
            "digest": "abc123"
        }
        
        field_info = DynamicFieldInfo.from_dict(original_data)
        converted_data = field_info.to_dict()
        
        assert converted_data == original_data
    
    def test_sui_object_data_round_trip(self):
        """Test SuiObjectData dictionary round trip."""
        original_data = {
            "objectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "version": 1,
            "digest": "abc123",
            "type": "0x2::coin::Coin<0x2::sui::SUI>",
            "owner": {
                "AddressOwner": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
            },
            "previousTransaction": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
            "storageRebate": 100
        }
        
        obj_data = SuiObjectData.from_dict(original_data)
        converted_data = obj_data.to_dict()
        
        assert converted_data == original_data
    
    def test_sui_event_round_trip(self):
        """Test SuiEvent dictionary round trip."""
        original_data = {
            "id": {
                "txDigest": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
                "eventSeq": "0"
            },
            "packageId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "transactionModule": "coin",
            "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "type": "0x2::coin::CoinCreated<0x2::sui::SUI>",
            "parsedJson": {
                "amount": "1000000000"
            },
            "timestampMs": 1234567890000
        }
        
        event = SuiEvent.from_dict(original_data)
        converted_data = event.to_dict()
        
        assert converted_data == original_data


class TestPaginationWithExtendedTypes:
    """Test pagination with Extended API types."""
    
    def test_page_with_dynamic_field_info(self):
        """Test Page with DynamicFieldInfo items."""
        field_data = [
            {
                "name": {"type": "u64", "value": 1},
                "bcsName": "0x01",
                "type": "DynamicField",
                "objectType": "test",
                "objectId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "version": 1,
                "digest": "abc123"
            }
        ]
        
        data = {
            "data": field_data,
            "hasNextPage": False
        }
        
        page = Page.from_dict(data, DynamicFieldInfo.from_dict)
        assert len(page) == 1
        assert isinstance(page[0], DynamicFieldInfo)
        assert page[0].name.value == 1
    
    def test_page_with_sui_events(self):
        """Test Page with SuiEvent items."""
        event_data = [
            {
                "id": {"txDigest": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF", "eventSeq": "0"},
                "packageId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "transactionModule": "test",
                "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "type": "test::Event"
            }
        ]
        
        data = {
            "data": event_data,
            "hasNextPage": True,
            "nextCursor": "cursor123"
        }
        
        page = Page.from_dict(data, SuiEvent.from_dict)
        assert len(page) == 1
        assert isinstance(page[0], SuiEvent)
        assert page[0].transaction_module == "test"
        assert page.has_next_page
        assert page.next_cursor == "cursor123" 