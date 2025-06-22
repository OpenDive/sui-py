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
import json
import asyncio
import websockets

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
        
        # Extract coffee_type from Move enum object
        coffee_type_data = data["coffee_type"]
        if isinstance(coffee_type_data, dict) and "variant" in coffee_type_data:
            self.coffee_type = coffee_type_data["variant"]  # Extract "Espresso" from {'variant': 'Espresso', 'fields': {}}
        else:
            self.coffee_type = str(coffee_type_data)  # Fallback for simple strings
            
        # Additional fields might be present
        self.cafe_id = data.get("cafe_id")
        self.customer = data.get("customer")


class CoffeeOrderUpdated:
    """Represents a CoffeeOrderUpdated event."""
    
    def __init__(self, data: Dict[str, Any]):
        self.order_id = data["order_id"]
        
        # Extract status from Move enum object
        status_data = data["status"]
        if isinstance(status_data, dict) and "variant" in status_data:
            self.status = status_data["variant"]  # Extract "Processing" from {'variant': 'Processing', 'fields': {}}
        else:
            self.status = str(status_data)  # Fallback for simple strings


class VoiceAgentNotifier:
    """WebSocket client for notifying voice agent of new coffee orders."""
    
    def __init__(self, enabled: bool = True, websocket_url: str = "ws://localhost:8765"):
        self.enabled = enabled
        self.websocket_url = websocket_url
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
    async def notify_new_order(self, order_id: str, coffee_type: str, priority: str = "normal") -> bool:
        """
        Send new order notification to voice agent via WebSocket.
        
        Args:
            order_id: Unique order identifier
            coffee_type: Type of coffee ordered
            priority: Priority level (normal, urgent, low)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Voice agent notifications disabled, skipping")
            return True
            
        message = {
            "type": "NEW_COFFEE_REQUEST",
            "order_id": order_id,
            "coffee_type": coffee_type,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"📡 Sending order notification to voice agent (attempt {attempt}/{self.max_retries})")
                
                # Connect to voice agent WebSocket server
                async with websockets.connect(
                    self.websocket_url,
                    ping_timeout=5,
                    close_timeout=5
                ) as websocket:
                    # Send notification
                    await websocket.send(json.dumps(message))
                    logger.info(f"📨 Sent: {message}")
                    
                    # Wait for confirmation
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data.get("status") == "success":
                        logger.info(f"✅ Voice agent confirmed order notification: {coffee_type} for order {order_id[:8]}...")
                        return True
                    else:
                        logger.warning(f"⚠️ Voice agent returned error: {response_data}")
                        return False
                        
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Timeout sending notification to voice agent (attempt {attempt}/{self.max_retries})")
            except websockets.exceptions.ConnectionRefused:
                logger.warning(f"🔌 Voice agent not available (attempt {attempt}/{self.max_retries})")
            except websockets.exceptions.WebSocketException as e:
                logger.warning(f"🌐 WebSocket error (attempt {attempt}/{self.max_retries}): {e}")
            except Exception as e:
                logger.error(f"❌ Unexpected error sending notification (attempt {attempt}/{self.max_retries}): {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay)
        
        logger.error(f"❌ Failed to notify voice agent after {self.max_retries} attempts")
        return False

    async def notify_order_update(self, order_id: str, coffee_type: str, status: str, priority: str = "normal") -> bool:
        """
        Send order status update notification to voice agent via WebSocket.
        
        Args:
            order_id: Unique order identifier
            coffee_type: Type of coffee ordered
            status: New order status (Ready, Processing, Completed, etc.)
            priority: Priority level (normal, urgent, low)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Voice agent notifications disabled, skipping")
            return True
            
        # Determine message type based on status
        if status == "Ready":
            message_type = "ORDER_READY"
        elif status == "Processing":
            message_type = "ORDER_PROCESSING"
        elif status == "Completed":
            message_type = "ORDER_COMPLETED"
        else:
            message_type = "ORDER_UPDATED"
        
        message = {
            "type": message_type,
            "order_id": order_id,
            "coffee_type": coffee_type,
            "status": status,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"📡 Sending order update notification to voice agent (attempt {attempt}/{self.max_retries})")
                
                # Connect to voice agent WebSocket server
                async with websockets.connect(
                    self.websocket_url,
                    ping_timeout=5,
                    close_timeout=5
                ) as websocket:
                    # Send notification
                    await websocket.send(json.dumps(message))
                    logger.info(f"📨 Sent update: {message}")
                    
                    # Wait for confirmation
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data.get("status") == "success":
                        logger.info(f"✅ Voice agent confirmed order update: {coffee_type} -> {status} for order {order_id[:8]}...")
                        return True
                    else:
                        logger.warning(f"⚠️ Voice agent returned error: {response_data}")
                        return False
                        
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Timeout sending update notification to voice agent (attempt {attempt}/{self.max_retries})")
            except websockets.exceptions.ConnectionRefused:
                logger.warning(f"🔌 Voice agent not available (attempt {attempt}/{self.max_retries})")
            except websockets.exceptions.WebSocketException as e:
                logger.warning(f"🌐 WebSocket error (attempt {attempt}/{self.max_retries}): {e}")
            except Exception as e:
                logger.error(f"❌ Unexpected error sending update notification (attempt {attempt}/{self.max_retries}): {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay)
        
        logger.error(f"❌ Failed to notify voice agent of order update after {self.max_retries} attempts")
        return False


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
        
        # Initialize voice agent notifier
        self.voice_agent_notifier = VoiceAgentNotifier(
            enabled=CONFIG.voice_agent.enabled,
            websocket_url=CONFIG.voice_agent.websocket_url
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
        
        # Notify voice agent of new order
        try:
            await self.voice_agent_notifier.notify_new_order(
                order_id=order_created.order_id,
                coffee_type=order_created.coffee_type,
                priority="normal"
            )
        except Exception as e:
            # Don't let voice agent notification failures affect order processing
            logger.error(f"⚠️ Failed to notify voice agent, but order processing continues: {e}")
    
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
        
        # Notify voice agent about order status update for important statuses
        if new_status in ["Ready", "Processing", "Completed"] and order.coffeeType:
            try:
                await self.voice_agent_notifier.notify_order_update(
                    order_id=order_id,
                    coffee_type=order.coffeeType,
                    status=new_status,
                    priority="urgent" if new_status == "Ready" else "normal"
                )
            except Exception as e:
                # Don't let voice agent notification failures affect order processing
                logger.error(f"⚠️ Failed to notify voice agent of order update, but processing continues: {e}")
        
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