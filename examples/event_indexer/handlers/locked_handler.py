"""
Locked object event handler for the SuiPy Event Indexer.

This module handles all events emitted by the 'lock' module of the swap contract,
processing lock creation and destruction events using typed SuiEvent objects.
"""

import logging
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

from sui_py import SuiEvent
from ..models import Locked
from ..config import CONFIG

logger = logging.getLogger(__name__)


class LockCreated:
    """Represents a LockCreated event."""
    
    def __init__(self, data: Dict[str, Any]):
        self.creator = data["creator"]
        self.lock_id = data["lock_id"]
        self.key_id = data["key_id"]
        self.item_id = data["item_id"]


class LockDestroyed:
    """Represents a LockDestroyed event."""
    
    def __init__(self, data: Dict[str, Any]):
        self.lock_id = data["lock_id"]


async def handle_lock_objects(events: List[SuiEvent], event_type: str, session: AsyncSession) -> None:
    """
    Handle all events emitted by the 'lock' module.
    
    Data is modeled in a way that allows writing to the DB in any order (DESC or ASC) without
    resulting in data inconsistencies. We construct updates to support multiple events involving
    a single record as part of the same batch of events.
    
    Args:
        events: List of typed SuiEvent objects
        event_type: The event type string for validation
        session: Database session for operations
    """
    if not events:
        return
    
    logger.info(f"Processing {len(events)} lock events")
    
    # Track updates by lock_id to handle multiple events for the same object
    updates: Dict[str, Dict[str, Any]] = {}
    
    for event in events:
        # Validate event origin
        if not event.type.startswith(event_type):
            logger.error(f"Invalid event module origin: {event.type} does not start with {event_type}")
            raise ValueError(f"Invalid event module origin: {event.type}")
        
        # Parse the event data
        if not event.parsed_json:
            logger.warning(f"Event {event.id} has no parsed JSON data, skipping")
            continue
        
        data = event.parsed_json
        
        # Determine lock_id from the event data
        lock_id = data.get("lock_id")
        if not lock_id:
            logger.warning(f"Event {event.id} missing lock_id, skipping")
            continue
        
        # Check if this is a deletion event (no key_id field)
        is_deletion_event = "key_id" not in data
        
        # Initialize update record if not exists
        if lock_id not in updates:
            updates[lock_id] = {
                "object_id": lock_id,
                "deleted": False
            }
        
        # Process different event types
        if is_deletion_event or event.type.endswith("::LockDestroyed") or "Destroyed" in event.type:
            logger.debug(f"Processing LockDestroyed for {lock_id}")
            lock_destroyed = LockDestroyed(data)
            updates[lock_id]["deleted"] = True
            
        elif event.type.endswith("::LockCreated") or "Created" in event.type:
            logger.debug(f"Processing LockCreated for {lock_id}")
            lock_created = LockCreated(data)
            updates[lock_id].update({
                "creator": lock_created.creator,
                "key_id": lock_created.key_id,
                "item_id": lock_created.item_id
            })
        else:
            logger.warning(f"Unknown lock event type: {event.type}")
    
    if not updates:
        logger.info("No valid lock updates to process")
        return
    
    # Perform database operations
    await _upsert_lock_records(session, list(updates.values()))
    
    logger.info(f"Successfully processed {len(updates)} lock object updates")


async def _upsert_lock_records(session: AsyncSession, records: List[Dict[str, Any]]) -> None:
    """
    Upsert lock records into the database.
    
    Uses database-specific upsert functionality for efficient bulk operations.
    For SQLite, we use individual upserts due to limited bulk upsert support.
    For PostgreSQL, we can use more efficient bulk upserts.
    
    Args:
        session: Database session
        records: List of lock record dictionaries
    """
    if not records:
        return
    
    # Determine database type from connection URL
    db_url = str(session.bind.url)
    
    if "sqlite" in db_url:
        await _upsert_lock_records_sqlite(session, records)
    elif "postgresql" in db_url:
        await _upsert_lock_records_postgresql(session, records)
    else:
        # Fallback to individual upserts
        await _upsert_lock_records_individual(session, records)


async def _upsert_lock_records_sqlite(session: AsyncSession, records: List[Dict[str, Any]]) -> None:
    """SQLite-specific upsert implementation."""
    for record in records:
        stmt = sqlite_insert(Locked).values(**record)
        stmt = stmt.on_conflict_do_update(
            index_elements=["object_id"],
            set_={
                key: stmt.excluded[key] 
                for key in record.keys() 
                if key != "object_id"
            }
        )
        await session.execute(stmt)
    
    await session.commit()


async def _upsert_lock_records_postgresql(session: AsyncSession, records: List[Dict[str, Any]]) -> None:
    """PostgreSQL-specific bulk upsert implementation."""
    if not records:
        return
    
    stmt = postgresql_insert(Locked).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=["object_id"],
        set_={
            "creator": stmt.excluded.creator,
            "key_id": stmt.excluded.key_id,
            "item_id": stmt.excluded.item_id,
            "deleted": stmt.excluded.deleted,
            "updated_at": stmt.excluded.updated_at
        }
    )
    await session.execute(stmt)
    await session.commit()


async def _upsert_lock_records_individual(session: AsyncSession, records: List[Dict[str, Any]]) -> None:
    """Fallback individual upsert implementation."""
    for record in records:
        # Check if record exists
        stmt = select(Locked).where(Locked.object_id == record["object_id"])
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing record
            for key, value in record.items():
                if key != "object_id":
                    setattr(existing, key, value)
        else:
            # Create new record
            locked = Locked(**record)
            session.add(locked)
    
    await session.commit() 