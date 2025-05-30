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
    Handle lock object events from the 'lock' module.
    
    Args:
        events: List of typed SuiEvent objects to process
        event_type: Type identifier for logging
        db: Prisma database connection
    """
    logger.info(f"🔒 LOCK HANDLER: Processing {len(events)} events of type {event_type}")
    
    # Collect updates keyed by lock object ID
    updates: Dict[str, Dict[str, Any]] = {}
    
    for i, event in enumerate(events):
        logger.debug(f"🔍 Processing lock event {i+1}/{len(events)}: {event.type}")
        
        # Validate event origin
        if not event.type.startswith(event_type):
            logger.error(f"Invalid event module origin: {event.type} does not start with {event_type}")
            raise ValueError(f"Invalid event module origin: {event.type}")
        
        # Parse the event data
        if not event.parsed_json:
            logger.warning(f"Event {event.id} has no parsed JSON data, skipping")
            continue
        
        data = event.parsed_json
        logger.debug(f"📊 Event data: {data}")
        
        # Determine lock_id from the event data (corrected field name)
        lock_id = data.get("lock_id")
        if not lock_id:
            # Try alternative field names in case the structure is different
            lock_id = data.get("locked_id") or data.get("id") or data.get("object_id")
            if not lock_id:
                logger.warning(f"Event {{'txDigest': '{event.id.tx_digest}', 'eventSeq': '{event.id.event_seq}'}} missing lock_id, skipping")
                continue
        
        logger.debug(f"🆔 Processing lock ID: {lock_id}")
        
        # Initialize update record if not exists
        if lock_id not in updates:
            updates[lock_id] = {
                "objectId": lock_id,
                "deleted": False
            }
        
        # Process different event types (corrected event type names)
        if event.type.endswith("::LockCreated") or "Created" in event.type:
            logger.info(f"🔐 Processing LockCreated for {lock_id}")
            lock_created = LockCreated(data)
            updates[lock_id].update({
                "creator": lock_created.creator,  # Fixed: use creator not sender
                "keyId": lock_created.key_id,
                "itemId": lock_created.item_id
            })
            
        elif event.type.endswith("::LockDestroyed") or "Destroyed" in event.type:
            logger.info(f"🔓 Processing LockDestroyed for {lock_id}")
            lock_destroyed = LockDestroyed(data)
            updates[lock_id]["deleted"] = True
        else:
            logger.warning(f"❓ Unknown lock event type: {event.type}")
    
    if not updates:
        logger.info("😴 No valid lock updates to process")
        return
    
    logger.info(f"💾 Saving {len(updates)} lock updates to database...")
    
    # Perform database operations using Prisma upserts
    for lock_data in updates.values():
        try:
            logger.debug(f"💾 Upserting lock: {lock_data['objectId']}")
            await db.locked.upsert(
                where={"objectId": lock_data["objectId"]},
                data={
                    "create": lock_data,
                    "update": {
                        key: value for key, value in lock_data.items() 
                        if key != "objectId"
                    }
                }
            )
        except Exception as e:
            logger.error(f"Failed to upsert lock {lock_data['objectId']}: {e}")
            raise
    
    logger.info(f"✅ Successfully processed {len(updates)} lock object updates") 