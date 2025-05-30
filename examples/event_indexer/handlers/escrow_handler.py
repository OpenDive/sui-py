"""
Escrow event handler for the SuiPy Event Indexer.

This module handles all events emitted by the 'shared' module of the swap contract,
processing escrow creation, swapping, and cancellation events using typed SuiEvent objects.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

from prisma import Prisma
from prisma.models import Escrow

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


async def handle_escrow_objects(events: List[SuiEvent], event_type: str, db: Prisma) -> None:
    """
    Handle escrow object events from the 'shared' module.
    
    Args:
        events: List of typed SuiEvent objects to process
        event_type: Type identifier for logging
        db: Prisma database connection
    """
    logger.info(f"🏪 ESCROW HANDLER: Processing {len(events)} events of type {event_type}")
    
    # Collect updates keyed by escrow object ID
    updates: Dict[str, Dict[str, Any]] = {}
    
    for i, event in enumerate(events):
        logger.debug(f"🔍 Processing escrow event {i+1}/{len(events)}: {event.type}")
        
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
        
        # Determine escrow_id from the event data
        escrow_id = data.get("escrow_id")
        if not escrow_id:
            logger.warning(f"Event {event.id} missing escrow_id, skipping")
            continue
        
        logger.debug(f"🆔 Processing escrow ID: {escrow_id}")
        
        # Initialize update record if not exists
        if escrow_id not in updates:
            updates[escrow_id] = {
                "objectId": escrow_id,
                "swapped": False,
                "cancelled": False
            }
        
        # Process different event types
        if event.type.endswith("::EscrowCancelled"):
            logger.info(f"❌ Processing EscrowCancelled for {escrow_id}")
            escrow_cancelled = EscrowCancelled(data)
            updates[escrow_id]["cancelled"] = True
            
        elif event.type.endswith("::EscrowSwapped"):
            logger.info(f"🔄 Processing EscrowSwapped for {escrow_id}")
            escrow_swapped = EscrowSwapped(data)
            updates[escrow_id]["swapped"] = True
            
        elif event.type.endswith("::EscrowCreated") or "Created" in event.type:
            logger.info(f"✨ Processing EscrowCreated for {escrow_id}")
            escrow_created = EscrowCreated(data)
            updates[escrow_id].update({
                "sender": escrow_created.sender,
                "recipient": escrow_created.recipient,
                "keyId": escrow_created.key_id,
                "itemId": escrow_created.item_id
            })
        else:
            logger.warning(f"❓ Unknown escrow event type: {event.type}")
    
    if not updates:
        logger.info("😴 No valid escrow updates to process")
        return
    
    logger.info(f"💾 Saving {len(updates)} escrow updates to database...")
    
    # Perform database operations using Prisma upserts
    for escrow_data in updates.values():
        try:
            logger.debug(f"💾 Upserting escrow: {escrow_data['objectId']}")
            await db.escrow.upsert(
                where={"objectId": escrow_data["objectId"]},
                data={
                    key: value for key, value in escrow_data.items() 
                    if key != "objectId"
                },
                create=escrow_data
            )
        except Exception as e:
            logger.error(f"Failed to upsert escrow {escrow_data['objectId']}: {e}")
            raise
    
    logger.info(f"✅ Successfully processed {len(updates)} escrow object updates") 