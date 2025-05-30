"""
Test script for the SuiPy Event Indexer.

This script tests the indexer components without requiring a real blockchain connection.
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, Any, List

from sqlalchemy import select

from sui_py import SuiEvent, SuiAddress, ObjectID
from .config import CONFIG
from .database import database
from .models import Cursor, Escrow, Locked
from .handlers import handle_escrow_objects, handle_lock_objects


# Mock event data for testing
MOCK_ESCROW_CREATED_EVENT = {
    "id": {
        "txDigest": "9jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
        "eventSeq": "0"
    },
    "packageId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "transactionModule": "shared",
    "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "type": f"{CONFIG.swap_contract.package_id}::shared::EscrowCreated",
    "parsedJson": {
        "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "recipient": "0x1111111111111111111111111111111111111111111111111111111111111111",
        "escrow_id": "0x2222222222222222222222222222222222222222222222222222222222222222",
        "key_id": "0x3333333333333333333333333333333333333333333333333333333333333333",
        "item_id": "0x4444444444444444444444444444444444444444444444444444444444444444"
    }
}

MOCK_ESCROW_SWAPPED_EVENT = {
    "id": {
        "txDigest": "8jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
        "eventSeq": "1"
    },
    "packageId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "transactionModule": "shared",
    "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "type": f"{CONFIG.swap_contract.package_id}::shared::EscrowSwapped",
    "parsedJson": {
        "escrow_id": "0x2222222222222222222222222222222222222222222222222222222222222222"
    }
}

MOCK_LOCK_CREATED_EVENT = {
    "id": {
        "txDigest": "7jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
        "eventSeq": "0"
    },
    "packageId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "transactionModule": "lock",
    "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "type": f"{CONFIG.swap_contract.package_id}::lock::LockCreated",
    "parsedJson": {
        "creator": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "lock_id": "0x5555555555555555555555555555555555555555555555555555555555555555",
        "key_id": "0x6666666666666666666666666666666666666666666666666666666666666666",
        "item_id": "0x7777777777777777777777777777777777777777777777777777777777777777"
    }
}

MOCK_LOCK_DESTROYED_EVENT = {
    "id": {
        "txDigest": "6jR9vbXjWaUbwg7aRKKHkZqZQYzFzFzFzFzFzFzFzF",
        "eventSeq": "1"
    },
    "packageId": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "transactionModule": "lock",
    "sender": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "type": f"{CONFIG.swap_contract.package_id}::lock::LockDestroyed",
    "parsedJson": {
        "lock_id": "0x5555555555555555555555555555555555555555555555555555555555555555"
    }
}


async def test_database_setup():
    """Test database setup and table creation."""
    print("Testing database setup...")
    
    # Use a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        test_db_url = f"sqlite+aiosqlite:///{tmp_file.name}"
        
        # Override database URL for testing
        original_url = CONFIG.database.url
        CONFIG.database.url = test_db_url
        
        try:
            # Create tables
            await database.create_tables()
            print("✓ Database tables created successfully")
            
            # Test session creation
            async with database.get_session() as session:
                # Test cursor operations
                cursor = Cursor(
                    id="test::module",
                    tx_digest="test_digest",
                    event_seq="0"
                )
                session.add(cursor)
                await session.commit()
                
                # Verify cursor was saved
                stmt = select(Cursor).where(Cursor.id == "test::module")
                result = await session.execute(stmt)
                saved_cursor = result.scalar_one_or_none()
                
                assert saved_cursor is not None
                assert saved_cursor.tx_digest == "test_digest"
                print("✓ Database operations working correctly")
                
        finally:
            # Restore original URL
            CONFIG.database.url = original_url
            # Clean up
            os.unlink(tmp_file.name)


async def test_escrow_handler():
    """Test escrow event handler."""
    print("Testing escrow event handler...")
    
    # Create mock events
    escrow_created = SuiEvent.from_dict(MOCK_ESCROW_CREATED_EVENT)
    escrow_swapped = SuiEvent.from_dict(MOCK_ESCROW_SWAPPED_EVENT)
    
    events = [escrow_created, escrow_swapped]
    event_type = f"{CONFIG.swap_contract.package_id}::shared"
    
    # Use temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        test_db_url = f"sqlite+aiosqlite:///{tmp_file.name}"
        original_url = CONFIG.database.url
        CONFIG.database.url = test_db_url
        
        try:
            await database.create_tables()
            
            async with database.get_session() as session:
                # Process events
                await handle_escrow_objects(events, event_type, session)
                
                # Verify escrow was created and updated
                stmt = select(Escrow).where(
                    Escrow.object_id == "0x2222222222222222222222222222222222222222222222222222222222222222"
                )
                result = await session.execute(stmt)
                escrow = result.scalar_one_or_none()
                
                assert escrow is not None
                assert escrow.sender == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
                assert escrow.recipient == "0x1111111111111111111111111111111111111111111111111111111111111111"
                assert escrow.swapped is True
                assert escrow.cancelled is False
                
                print("✓ Escrow events processed correctly")
                
        finally:
            CONFIG.database.url = original_url
            os.unlink(tmp_file.name)


async def test_lock_handler():
    """Test lock event handler."""
    print("Testing lock event handler...")
    
    # Create mock events
    lock_created = SuiEvent.from_dict(MOCK_LOCK_CREATED_EVENT)
    lock_destroyed = SuiEvent.from_dict(MOCK_LOCK_DESTROYED_EVENT)
    
    events = [lock_created, lock_destroyed]
    event_type = f"{CONFIG.swap_contract.package_id}::lock"
    
    # Use temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        test_db_url = f"sqlite+aiosqlite:///{tmp_file.name}"
        original_url = CONFIG.database.url
        CONFIG.database.url = test_db_url
        
        try:
            await database.create_tables()
            
            async with database.get_session() as session:
                # Process events
                await handle_lock_objects(events, event_type, session)
                
                # Verify lock was created and deleted
                stmt = select(Locked).where(
                    Locked.object_id == "0x5555555555555555555555555555555555555555555555555555555555555555"
                )
                result = await session.execute(stmt)
                lock = result.scalar_one_or_none()
                
                assert lock is not None
                assert lock.creator == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
                assert lock.key_id == "0x6666666666666666666666666666666666666666666666666666666666666666"
                assert lock.deleted is True
                
                print("✓ Lock events processed correctly")
                
        finally:
            CONFIG.database.url = original_url
            os.unlink(tmp_file.name)


async def test_type_safety():
    """Test type safety of event processing."""
    print("Testing type safety...")
    
    # Test SuiEvent creation and validation
    event = SuiEvent.from_dict(MOCK_ESCROW_CREATED_EVENT)
    
    # Verify typed fields
    assert isinstance(event.sender, SuiAddress)
    assert isinstance(event.package_id, ObjectID)
    assert event.type == f"{CONFIG.swap_contract.package_id}::shared::EscrowCreated"
    assert event.parsed_json is not None
    
    print("✓ Type safety working correctly")


async def run_all_tests():
    """Run all tests."""
    print("Running SuiPy Event Indexer Tests")
    print("=" * 40)
    
    try:
        await test_database_setup()
        await test_escrow_handler()
        await test_lock_handler()
        await test_type_safety()
        
        print("\n" + "=" * 40)
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise during testing
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(run_all_tests()) 