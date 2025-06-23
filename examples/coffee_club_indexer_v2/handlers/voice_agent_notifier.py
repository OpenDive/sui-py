"""
Voice Agent Notifier for the Coffee Club Event Indexer.

This module provides WebSocket-based communication with a voice agent,
allowing the coffee system to send notifications about new orders and
order status updates.
"""

import logging
import sys
import json
import asyncio
import websockets
from datetime import datetime
from pathlib import Path
from typing import Optional

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