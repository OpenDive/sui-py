"""
Locked object event handler for the SuiPy Event Indexer.

This module handles all events emitted by the 'lock' module of the swap contract,
processing lock creation and destruction events using typed SuiEvent objects.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

from prisma import Prisma
from prisma.models import Locked

from sui_py import SuiEvent

# Handle both direct script execution and module import
try:
    from config import CONFIG
except ImportError:
    # Add parent directory to path for direct execution
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    try:
        from config import CONFIG
    except ImportError:
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


async def handle_lock_objects(events: List[SuiEvent], event_type: str, db: Prisma) -> None:
    """
    Handle all events emitted by the 'lock' module.
    
    Data is modeled in a way that allows writing to the DB in any order (DESC or ASC) without
    resulting in data inconsistencies. We construct updates to support multiple events involving
    a single record as part of the same batch of events.
    
    Args:
        events: List of typed SuiEvent objects
        event_type: The event type string for validation
        db: Prisma database client
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
                "objectId": lock_id,
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
                "keyId": lock_created.key_id,
                "itemId": lock_created.item_id
            })
        else:
            logger.warning(f"Unknown lock event type: {event.type}")
    
    if not updates:
        logger.info("No valid lock updates to process")
        return
    
    # Perform database operations using Prisma upserts
    for lock_data in updates.values():
        try:
            await db.locked.upsert(
                where={"objectId": lock_data["objectId"]},
                data={
                    key: value for key, value in lock_data.items() 
                    if key != "objectId"
                },
                create=lock_data
            )
        except Exception as e:
            logger.error(f"Failed to upsert lock {lock_data['objectId']}: {e}")
            raise
    
    logger.info(f"Successfully processed {len(updates)} lock object updates") 