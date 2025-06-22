"""
Basic tests for the Coffee Club Event Indexer.

This module contains simple tests to validate the coffee club indexer
components and configuration.
"""

import pytest
from unittest.mock import Mock, patch
import asyncio
from pathlib import Path

# Import components to test
from config import CONFIG, CoffeeClubContract, CoffeeMachine
from coffee_machine.controller import CoffeeMachineController


class TestConfiguration:
    """Test configuration loading and validation."""
    
    def test_config_has_required_fields(self):
        """Test that config has all required fields."""
        assert hasattr(CONFIG, 'network')
        assert hasattr(CONFIG, 'rpc_url')
        assert hasattr(CONFIG, 'coffee_club_contract')
        assert hasattr(CONFIG, 'coffee_machine')
        assert hasattr(CONFIG, 'database_url')
    
    def test_coffee_club_contract_config(self):
        """Test coffee club contract configuration."""
        assert isinstance(CONFIG.coffee_club_contract, CoffeeClubContract)
        assert hasattr(CONFIG.coffee_club_contract, 'package_id')
    
    def test_coffee_machine_config(self):
        """Test coffee machine configuration."""
        assert isinstance(CONFIG.coffee_machine, CoffeeMachine)
        assert hasattr(CONFIG.coffee_machine, 'mac_address')
        assert hasattr(CONFIG.coffee_machine, 'controller_path')
        assert hasattr(CONFIG.coffee_machine, 'enabled')
    
    def test_valid_coffee_types(self):
        """Test that valid coffee types are defined."""
        assert hasattr(CONFIG, 'valid_coffee_types')
        assert isinstance(CONFIG.valid_coffee_types, list)
        assert 'espresso' in CONFIG.valid_coffee_types
        assert 'americano' in CONFIG.valid_coffee_types


class TestCoffeeMachineController:
    """Test coffee machine controller functionality."""
    
    def test_controller_initialization(self):
        """Test controller initialization."""
        controller = CoffeeMachineController(
            mac_address="AA:BB:CC:DD:EE:FF",
            controller_path="/fake/path/controller.py",
            enabled=True
        )
        
        assert controller.mac_address == "AA:BB:CC:DD:EE:FF"
        assert controller.controller_path == "/fake/path/controller.py"
        assert controller.enabled == False  # Should be disabled due to invalid path
    
    def test_coffee_type_validation(self):
        """Test coffee type validation."""
        controller = CoffeeMachineController(
            mac_address="AA:BB:CC:DD:EE:FF",
            controller_path="/fake/path/controller.py",
            enabled=False
        )
        
        valid_types = ['espresso', 'americano', 'doppio']
        
        assert controller.is_valid_coffee_type('espresso', valid_types)
        assert controller.is_valid_coffee_type('ESPRESSO', valid_types)
        assert not controller.is_valid_coffee_type('invalid', valid_types)
    
    def test_coffee_type_extraction(self):
        """Test coffee type extraction from order object."""
        controller = CoffeeMachineController(
            mac_address="AA:BB:CC:DD:EE:FF",
            controller_path="/fake/path/controller.py",
            enabled=False
        )
        
        valid_types = ['espresso', 'americano', 'doppio']
        
        # Test format 1: { variant: "Espresso" }
        order_object_1 = {
            "data": {
                "content": {
                    "fields": {
                        "coffee_type": {"variant": "Espresso"}
                    }
                }
            }
        }
        result = controller.extract_coffee_type(order_object_1, valid_types)
        assert result == "espresso"
        
        # Test format 2: { fields: { name: "Americano" } }
        order_object_2 = {
            "data": {
                "content": {
                    "fields": {
                        "coffee_type": {"fields": {"name": "Americano"}}
                    }
                }
            }
        }
        result = controller.extract_coffee_type(order_object_2, valid_types)
        assert result == "americano"
        
        # Test format 3: "Doppio" (string directly)
        order_object_3 = {
            "data": {
                "content": {
                    "fields": {
                        "coffee_type": "Doppio"
                    }
                }
            }
        }
        result = controller.extract_coffee_type(order_object_3, valid_types)
        assert result == "doppio"
        
        # Test invalid coffee type
        order_object_invalid = {
            "data": {
                "content": {
                    "fields": {
                        "coffee_type": "Invalid"
                    }
                }
            }
        }
        result = controller.extract_coffee_type(order_object_invalid, valid_types, "default")
        assert result == "default"
    
    @pytest.mark.asyncio
    async def test_make_coffee_disabled(self):
        """Test coffee making when controller is disabled."""
        controller = CoffeeMachineController(
            mac_address="AA:BB:CC:DD:EE:FF",
            controller_path="/fake/path/controller.py",
            enabled=False
        )
        
        result = await controller.make_coffee("espresso", "order_123")
        assert result == False


class TestEventHandlers:
    """Test event handler imports and basic functionality."""
    
    def test_handler_imports(self):
        """Test that handlers can be imported."""
        try:
            from handlers import handle_cafe_events, handle_order_events
            assert callable(handle_cafe_events)
            assert callable(handle_order_events)
        except ImportError as e:
            pytest.fail(f"Failed to import handlers: {e}")


class TestIndexer:
    """Test indexer initialization and configuration."""
    
    def test_indexer_import(self):
        """Test that indexer can be imported."""
        try:
            from indexer import CoffeeClubIndexer
            indexer = CoffeeClubIndexer()
            assert indexer.limit == CONFIG.batch_size
            assert len(indexer.events_to_track) == 3  # CafeCreated, OrderCreated, OrderUpdated
        except ImportError as e:
            pytest.fail(f"Failed to import indexer: {e}")


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"]) 