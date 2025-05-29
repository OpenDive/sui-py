"""
Escrow event handler for the SuiPy Event Indexer.

This module handles all events emitted by the 'shared' module of the swap contract,
processing escrow creation, swapping, and cancellation events using typed SuiEvent objects.
"""

import logging
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

from sui_py import SuiEvent
from ..models import Escrow
from ..config import CONFIG

logger = logging.getLogger(__name__)


class EscrowCreated:
    """Represents an EscrowCreated event."""
    
    def __init__(self, data: Dict[str, Any]):
        self.sender = data["sender"]
        self.recipient = data["recipient"]
        self.escrow_id = data["escrow_id"]
        self.key_id = data["key_id"]
        self.item_id = data["item_id"]


class EscrowSwapped:
    """Represents an EscrowSwapped event."""
    
    def __init__(self, data: Dict[str, Any]):
        self.escrow_id = data["escrow_id"]


class EscrowCancelled:
    """Represents an EscrowCancelled event."""
    
    def __init__(self, data: Dict[str, Any]):
        self.escrow_id = data["escrow_id"]


async def handle_escrow_objects(events: List[SuiEvent], event_type: str, session: AsyncSession) -> None:
    """
    Handle all events emitted by the 'shared' module.
    
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
    
    logger.info(f"Processing {len(events)} escrow events")
    
    # Track updates by escrow_id to handle multiple events for the same object
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
        
        # Determine escrow_id from the event data
        escrow_id = data.get("escrow_id")
        if not escrow_id:
            logger.warning(f"Event {event.id} missing escrow_id, skipping")
            continue
        
        # Initialize update record if not exists
        if escrow_id not in updates:
            updates[escrow_id] = {
                "object_id": escrow_id,
                "swapped": False,
                "cancelled": False
            }
        
        # Process different event types
        if event.type.endswith("::EscrowCancelled"):
            logger.debug(f"Processing EscrowCancelled for {escrow_id}")
            escrow_cancelled = EscrowCancelled(data)
            updates[escrow_id]["cancelled"] = True
            
        elif event.type.endswith("::EscrowSwapped"):
            logger.debug(f"Processing EscrowSwapped for {escrow_id}")
            escrow_swapped = EscrowSwapped(data)
            updates[escrow_id]["swapped"] = True
            
        elif event.type.endswith("::EscrowCreated") or "Created" in event.type:
            logger.debug(f"Processing EscrowCreated for {escrow_id}")
            escrow_created = EscrowCreated(data)
            updates[escrow_id].update({
                "sender": escrow_created.sender,
                "recipient": escrow_created.recipient,
                "key_id": escrow_created.key_id,
                "item_id": escrow_created.item_id
            })
        else:
            logger.warning(f"Unknown escrow event type: {event.type}")
    
    if not updates:
        logger.info("No valid escrow updates to process")
        return
    
    # Perform database operations
    await _upsert_escrow_records(session, list(updates.values()))
    
    logger.info(f"Successfully processed {len(updates)} escrow object updates")


async def _upsert_escrow_records(session: AsyncSession, records: List[Dict[str, Any]]) -> None:
    """
    Upsert escrow records into the database.
    
    Uses database-specific upsert functionality for efficient bulk operations.
    For SQLite, we use individual upserts due to limited bulk upsert support.
    For PostgreSQL, we can use more efficient bulk upserts.
    
    Args:
        session: Database session
        records: List of escrow record dictionaries
    """
    if not records:
        return
    
    # Determine database type from connection URL
    db_url = str(session.bind.url)
    
    if "sqlite" in db_url:
        await _upsert_escrow_records_sqlite(session, records)
    elif "postgresql" in db_url:
        await _upsert_escrow_records_postgresql(session, records)
    else:
        # Fallback to individual upserts
        await _upsert_escrow_records_individual(session, records)


async def _upsert_escrow_records_sqlite(session: AsyncSession, records: List[Dict[str, Any]]) -> None:
    """SQLite-specific upsert implementation."""
    for record in records:
        stmt = sqlite_insert(Escrow).values(**record)
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


async def _upsert_escrow_records_postgresql(session: AsyncSession, records: List[Dict[str, Any]]) -> None:
    """PostgreSQL-specific bulk upsert implementation."""
    if not records:
        return
    
    stmt = postgresql_insert(Escrow).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=["object_id"],
        set_={
            "sender": stmt.excluded.sender,
            "recipient": stmt.excluded.recipient,
            "key_id": stmt.excluded.key_id,
            "item_id": stmt.excluded.item_id,
            "swapped": stmt.excluded.swapped,
            "cancelled": stmt.excluded.cancelled,
            "updated_at": stmt.excluded.updated_at
        }
    )
    await session.execute(stmt)
    await session.commit()


async def _upsert_escrow_records_individual(session: AsyncSession, records: List[Dict[str, Any]]) -> None:
    """Fallback individual upsert implementation."""
    for record in records:
        # Check if record exists
        stmt = select(Escrow).where(Escrow.object_id == record["object_id"])
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing record
            for key, value in record.items():
                if key != "object_id":
                    setattr(existing, key, value)
        else:
            # Create new record
            escrow = Escrow(**record)
            session.add(escrow)
    
    await session.commit() 