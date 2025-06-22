"""
Order event handler for the Coffee Club Event Indexer.

This module handles CoffeeOrderCreated and CoffeeOrderUpdated events emitted by the 
coffee club contract, processing order lifecycle events and triggering coffee machine
operations when orders reach the "Processing" status.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from prisma import Prisma
from prisma.models import CoffeeOrder

from sui_py import SuiClient, SuiEvent

# Handle both direct script execution and module import
try:
    from config import CONFIG
    from coffee_machine import CoffeeMachineController
except ImportError:
    # Add parent directory to path for direct execution
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    try:
        from config import CONFIG
        from coffee_machine import CoffeeMachineController
    except ImportError:
        from ..config import CONFIG
        from ..coffee_machine import CoffeeMachineController

logger = logging.getLogger(__name__)


class CoffeeOrderCreated:
    """Represents a CoffeeOrderCreated event."""
    
    def __init__(self, data: Dict[str, Any]):
        self.order_id = data["order_id"]
        self.coffee_type = data["coffee_type"]  # NEW: Available in event
        # Additional fields might be present
        self.cafe_id = data.get("cafe_id")
        self.customer = data.get("customer")


class CoffeeOrderUpdated:
    """Represents a CoffeeOrderUpdated event."""
    
    def __init__(self, data: Dict[str, Any]):
        self.order_id = data["order_id"]
        self.status = data["status"]  # NEW: Available directly in event


class OrderProcessor:
    """Processes coffee orders and manages coffee machine integration."""
    
    def __init__(self, client: SuiClient, db: Prisma):
        self.client = client
        self.db = db
        self.coffee_machine = CoffeeMachineController(
            mac_address=CONFIG.coffee_machine.mac_address,
            controller_path=CONFIG.coffee_machine.controller_path,
            enabled=CONFIG.coffee_machine.enabled
        )
    
    async def process_order_created(self, order_created: CoffeeOrderCreated) -> None:
        """Process a newly created coffee order."""
        logger.info(f"☕ Creating new order {order_created.order_id}")
        
        await self.db.coffeeorder.upsert(
            where={"objectId": order_created.order_id},
            data={
                "create": {
                    "objectId": order_created.order_id,
                    "status": "Created",
                    "coffeeType": order_created.coffee_type,  # NEW: Store coffee type from event
                    "createdAt": datetime.now(),
                },
                "update": {
                    # Don't update existing orders on creation events
                }
            }
        )
        
        logger.info(f"✅ Successfully created order {order_created.order_id}")
    
    async def process_order_updated(self, order_updated: CoffeeOrderUpdated) -> None:
        """Process an updated coffee order and trigger coffee machine if needed."""
        order_id = order_updated.order_id
        new_status = order_updated.status
        logger.info(f"🔄 Processing order update for {order_id} to status {new_status}")
        
        # Get current order from database to check for duplicates and get coffee type
        order = await self.db.coffeeorder.find_unique(
            where={"objectId": order_id}
        )
        
        if not order:
            logger.error(f"❌ Order {order_id} not found in database")
            return
        
        # Check if the order is already at this status to avoid duplicates
        if order.status == new_status:
            logger.info(f"⚠️ Order {order_id} already has status {new_status}, skipping")
            return
        
        # Update order status in database (no blockchain fetch needed!)
        await self.db.coffeeorder.update(
            where={"objectId": order_id},
            data={
                "status": new_status,
                "updatedAt": datetime.now(),
            }
        )
        
        logger.info(f"📊 Updated order {order_id} status to {new_status}")
        
        # If status is "Processing", trigger coffee machine using stored coffee type
        if new_status == "Processing" and order.coffeeType:
            await self._trigger_coffee_machine_simple(order_id, order.coffeeType)
    
    async def _trigger_coffee_machine_simple(self, order_id: str, coffee_type: str) -> None:
        """Simplified coffee machine trigger using stored coffee_type."""
        logger.info(f"🚀 Triggering coffee machine for order {order_id}")
        
        try:
            # Map coffee type enum to machine command
            coffee_type_mapped = self._map_coffee_type(coffee_type)
            
            logger.info(f"☕ Making {coffee_type_mapped} for order {order_id}")
            
            # Trigger coffee machine
            success = await self.coffee_machine.make_coffee(coffee_type_mapped, order_id)
            
            if success:
                logger.info(f"✅ Successfully triggered coffee machine for order {order_id}")
            else:
                logger.error(f"❌ Failed to trigger coffee machine for order {order_id}")
                
        except Exception as e:
            logger.error(f"❌ Error triggering coffee machine for order {order_id}: {e}")
    
    def _map_coffee_type(self, coffee_type: str) -> str:
        """Map new CoffeeType enum values to machine commands."""
        mapping = {
            "Espresso": "espresso",
            "Americano": "americano", 
            "Doppio": "doppio",      # NEW
            "Long": "long",          # NEW
            "HotWater": "hotwater",  # NEW  
            "Coffee": "coffee"       # NEW
        }
        return mapping.get(coffee_type, "espresso")  # Default fallback
    
    async def _trigger_coffee_machine(self, order_id: str, order_data: Any) -> None:
        """Trigger the coffee machine for a processing order."""
        logger.info(f"🚀 Triggering coffee machine for order {order_id}")
        
        try:
            # Extract coffee type from order data
            coffee_type = self.coffee_machine.extract_coffee_type(
                {"data": order_data},
                CONFIG.valid_coffee_types,
                default="espresso"
            )
            
            logger.info(f"☕ Making {coffee_type} for order {order_id}")
            
            # Trigger coffee machine
            success = await self.coffee_machine.make_coffee(coffee_type, order_id)
            
            if success:
                logger.info(f"✅ Successfully triggered coffee machine for order {order_id}")
            else:
                logger.error(f"❌ Failed to trigger coffee machine for order {order_id}")
                
        except Exception as e:
            logger.error(f"❌ Error triggering coffee machine for order {order_id}: {e}")


async def handle_order_events(events: List[SuiEvent], event_type: str, db: Prisma) -> None:
    """
    Handle coffee order events from the coffee club contract.
    
    Args:
        events: List of typed SuiEvent objects to process
        event_type: Type identifier for logging
        db: Prisma database connection
    """
    logger.info(f"☕ ORDER HANDLER: Processing {len(events)} order events of type {event_type}")
    
    # Initialize SUI client for order processing
    from sui_py import SuiClient
    client = SuiClient(CONFIG.rpc_url)
    await client.connect()
    
    try:
        # Initialize order processor
        processor = OrderProcessor(client, db)
        
        for i, event in enumerate(events):
            logger.debug(f"🔍 Processing order event {i+1}/{len(events)}: {event.type}")
            
            # Validate event origin
            if not event.type.startswith(event_type):
                logger.error(f"Invalid event module origin: {event.type} does not start with {event_type}")
                raise ValueError(f"Invalid event module origin: {event.type}")
            
            # Parse the event data
            if not event.parsed_json:
                logger.warning(f"Event {event.id} has no parsed JSON data, skipping")
                continue
            
            data = event.parsed_json
            logger.info(f"📊 RAW ORDER EVENT DATA: {data}")
            logger.info(f"📊 Event type: {event.type}")
            if "coffee_type" in data:
                logger.info(f"📊 Raw coffee_type: {data['coffee_type']} (type: {type(data['coffee_type'])})")
            if "status" in data:
                logger.info(f"📊 Raw status: {data['status']} (type: {type(data['status'])})")
            
            try:
                # Handle different order event types
                if event.type.endswith("::CoffeeOrderCreated") or "CoffeeOrderCreated" in event.type:
                    order_created = CoffeeOrderCreated(data)
                    await processor.process_order_created(order_created)
                    
                elif event.type.endswith("::CoffeeOrderUpdated") or "CoffeeOrderUpdated" in event.type:
                    order_updated = CoffeeOrderUpdated(data)
                    await processor.process_order_updated(order_updated)
                    
                else:
                    logger.info(f"🚫 Skipping unknown order event type: {event.type}")
                    continue
                    
            except KeyError as e:
                logger.error(f"❌ Missing required field in order event {event.id}: {e}")
                continue
            except Exception as e:
                logger.error(f"❌ Error processing order event {event.id}: {e}")
                raise
    
    finally:
        # Clean up client connection
        await client.close()
    
    logger.info(f"🎉 Successfully processed {len(events)} order events") 