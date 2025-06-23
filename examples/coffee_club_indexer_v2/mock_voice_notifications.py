#!/usr/bin/env python3
"""
Mock Voice Notification System for Coffee Club Event Indexer.

This module provides a MockNotificationGenerator for testing voice agent integration
without requiring real blockchain events. It can simulate various order scenarios
including single orders, rush periods, and mixed coffee types.

Usage:
    # As a module
    from mock_voice_notifications import MockNotificationGenerator
    generator = MockNotificationGenerator()
    await generator.simulate_order_lifecycle()
    
    # As a standalone script
    python mock_voice_notifications.py --scenario rush_period --orders 5 --delay 2
"""

import argparse
import asyncio
import logging
import random
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Handle both direct script execution and module import
try:
    from config import CONFIG
    from handlers.voice_agent_notifier import VoiceAgentNotifier
except ImportError:
    # Add current directory to path for direct execution
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    try:
        from config import CONFIG
        from handlers.voice_agent_notifier import VoiceAgentNotifier
    except ImportError:
        # Try relative imports
        from .config import CONFIG
        from .handlers.voice_agent_notifier import VoiceAgentNotifier

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockNotificationGenerator:
    """Generator for mock voice agent notifications to test the coffee system."""
    
    def __init__(self, 
                 voice_agent_url: Optional[str] = None,
                 enabled: bool = True):
        """
        Initialize the mock notification generator.
        
        Args:
            voice_agent_url: WebSocket URL for voice agent (defaults to config)
            enabled: Whether notifications are enabled (defaults to True for testing)
        """
        self.voice_agent_url = voice_agent_url or CONFIG.voice_agent.websocket_url
        self.enabled = enabled
        
        # Initialize voice agent notifier
        self.notifier = VoiceAgentNotifier(
            enabled=self.enabled,
            websocket_url=self.voice_agent_url
        )
        
        # Coffee types from config (map to Move enum variants)
        self.coffee_types = [
            "Espresso",
            "Americano", 
            "Doppio",
            "Long",
            "Coffee",
            "HotWater"
        ]
        
        # Order statuses for lifecycle simulation
        self.order_statuses = ["Created", "Processing", "Ready", "Completed"]
        
        # Priorities for different scenarios
        self.priorities = ["low", "normal", "urgent"]
    
    def _generate_order_id(self) -> str:
        """Generate a realistic-looking order ID."""
        return f"0x{uuid.uuid4().hex[:16]}"
    
    def _random_coffee_type(self) -> str:
        """Get a random coffee type."""
        return random.choice(self.coffee_types)
    
    def _random_priority(self) -> str:
        """Get a random priority level."""
        return random.choice(self.priorities)
    
    async def simulate_single_order(self, 
                                   coffee_type: Optional[str] = None,
                                   order_id: Optional[str] = None,
                                   priority: str = "normal",
                                   delay_between_status: float = 2.0) -> str:
        """
        Simulate a complete single order lifecycle.
        
        Args:
            coffee_type: Type of coffee (random if None)
            order_id: Order ID (generated if None)
            priority: Priority level
            delay_between_status: Delay in seconds between status updates
            
        Returns:
            The order ID that was simulated
        """
        coffee_type = coffee_type or self._random_coffee_type()
        order_id = order_id or self._generate_order_id()
        
        logger.info(f"🎭 Starting mock order simulation: {coffee_type} (Order: {order_id[:8]}...)")
        
        try:
            # 1. New order notification
            logger.info(f"☕ Simulating new order: {coffee_type}")
            success = await self.notifier.notify_new_order(
                order_id=order_id,
                coffee_type=coffee_type,
                priority=priority
            )
            
            if success:
                logger.info(f"✅ New order notification sent successfully")
            else:
                logger.warning(f"⚠️ New order notification failed")
            
            # Delay before status updates
            await asyncio.sleep(delay_between_status)
            
            # 2. Order status updates
            for status in ["Processing", "Ready", "Completed"]:
                logger.info(f"📊 Simulating order update: {order_id[:8]}... -> {status}")
                
                # Adjust priority based on status
                current_priority = "urgent" if status == "Ready" else priority
                
                success = await self.notifier.notify_order_update(
                    order_id=order_id,
                    coffee_type=coffee_type,
                    status=status,
                    priority=current_priority
                )
                
                if success:
                    logger.info(f"✅ Order update notification sent: {status}")
                else:
                    logger.warning(f"⚠️ Order update notification failed: {status}")
                
                # Delay before next status (except for last one)
                if status != "Completed":
                    await asyncio.sleep(delay_between_status)
            
            logger.info(f"🎉 Mock order simulation completed: {order_id[:8]}...")
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Error in mock order simulation: {e}")
            raise
    
    async def simulate_order_lifecycle(self, 
                                     coffee_type: Optional[str] = None,
                                     delay: float = 2.0) -> str:
        """
        Simulate a single order lifecycle (alias for simulate_single_order).
        
        Args:
            coffee_type: Type of coffee (random if None)
            delay: Delay between status updates
            
        Returns:
            The order ID that was simulated
        """
        return await self.simulate_single_order(
            coffee_type=coffee_type,
            delay_between_status=delay
        )
    
    async def simulate_rush_period(self, 
                                  num_orders: int = 5,
                                  delay_between_orders: float = 1.0,
                                  delay_between_status: float = 1.5) -> List[str]:
        """
        Simulate a busy rush period with multiple concurrent orders.
        
        Args:
            num_orders: Number of orders to simulate
            delay_between_orders: Delay between starting each order
            delay_between_status: Delay between status updates within an order
            
        Returns:
            List of order IDs that were simulated
        """
        logger.info(f"🏃 Starting rush period simulation: {num_orders} orders")
        
        order_tasks = []
        order_ids = []
        
        try:
            # Start orders with staggered timing
            for i in range(num_orders):
                coffee_type = self._random_coffee_type()
                priority = "urgent" if i < 2 else self._random_priority()  # First 2 orders are urgent
                
                logger.info(f"📋 Queuing order {i+1}/{num_orders}: {coffee_type} ({priority})")
                
                # Create task for this order
                task = asyncio.create_task(
                    self.simulate_single_order(
                        coffee_type=coffee_type,
                        priority=priority,
                        delay_between_status=delay_between_status
                    )
                )
                order_tasks.append(task)
                
                # Store order ID (will be available when task completes)
                # For now we'll collect them after all tasks complete
                
                # Delay before starting next order
                if i < num_orders - 1:
                    await asyncio.sleep(delay_between_orders)
            
            # Wait for all orders to complete
            logger.info(f"⏳ Waiting for all {num_orders} orders to complete...")
            order_ids = await asyncio.gather(*order_tasks)
            
            logger.info(f"🎉 Rush period simulation completed: {len(order_ids)} orders processed")
            return order_ids
            
        except Exception as e:
            logger.error(f"❌ Error in rush period simulation: {e}")
            # Cancel remaining tasks
            for task in order_tasks:
                if not task.done():
                    task.cancel()
            raise
    
    async def simulate_mixed_coffee_types(self, 
                                        delay: float = 1.0) -> List[str]:
        """
        Simulate one order of each coffee type.
        
        Args:
            delay: Delay between each order
            
        Returns:
            List of order IDs that were simulated
        """
        logger.info(f"🌈 Starting mixed coffee types simulation: {len(self.coffee_types)} types")
        
        order_ids = []
        
        try:
            for i, coffee_type in enumerate(self.coffee_types):
                logger.info(f"☕ Simulating {coffee_type} ({i+1}/{len(self.coffee_types)})")
                
                order_id = await self.simulate_single_order(
                    coffee_type=coffee_type,
                    priority="normal",
                    delay_between_status=1.0
                )
                order_ids.append(order_id)
                
                # Delay before next coffee type
                if i < len(self.coffee_types) - 1:
                    await asyncio.sleep(delay)
            
            logger.info(f"🎉 Mixed coffee types simulation completed: {len(order_ids)} orders")
            return order_ids
            
        except Exception as e:
            logger.error(f"❌ Error in mixed coffee types simulation: {e}")
            raise
    
    async def simulate_error_scenarios(self) -> None:
        """
        Simulate various error scenarios to test system resilience.
        """
        logger.info("🚨 Starting error scenario simulation")
        
        # Test with invalid WebSocket URL
        logger.info("Testing with invalid WebSocket URL...")
        invalid_notifier = VoiceAgentNotifier(
            enabled=True,
            websocket_url="ws://invalid-host:9999"
        )
        
        success = await invalid_notifier.notify_new_order(
            order_id=self._generate_order_id(),
            coffee_type="Espresso",
            priority="normal"
        )
        
        if not success:
            logger.info("✅ Correctly handled invalid WebSocket URL")
        else:
            logger.warning("⚠️ Unexpected success with invalid URL")
        
        # Test with disabled notifier
        logger.info("Testing with disabled notifier...")
        disabled_notifier = VoiceAgentNotifier(enabled=False)
        
        success = await disabled_notifier.notify_new_order(
            order_id=self._generate_order_id(),
            coffee_type="Americano",
            priority="normal"
        )
        
        if success:
            logger.info("✅ Correctly handled disabled notifier")
        else:
            logger.warning("⚠️ Disabled notifier should return True")
        
        logger.info("🎉 Error scenario simulation completed")


async def main():
    """Main function for standalone script execution."""
    parser = argparse.ArgumentParser(
        description="Mock Voice Notification System for Coffee Club",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mock_voice_notifications.py --scenario single --coffee Espresso --delay 3
  python mock_voice_notifications.py --scenario rush_period --orders 10 --delay 0.5
  python mock_voice_notifications.py --scenario mixed --delay 2
  python mock_voice_notifications.py --scenario errors
        """
    )
    
    parser.add_argument(
        "--scenario",
        choices=["single", "rush_period", "mixed", "errors"],
        default="single",
        help="Simulation scenario to run (default: single)"
    )
    
    parser.add_argument(
        "--coffee",
        choices=["Espresso", "Americano", "Doppio", "Long", "Coffee", "HotWater"],
        help="Coffee type for single order (random if not specified)"
    )
    
    parser.add_argument(
        "--orders",
        type=int,
        default=5,
        help="Number of orders for rush period scenario (default: 5)"
    )
    
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between operations in seconds (default: 2.0)"
    )
    
    parser.add_argument(
        "--websocket-url",
        default=None,
        help=f"Voice agent WebSocket URL (default: {CONFIG.voice_agent.websocket_url})"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize generator
    generator = MockNotificationGenerator(
        voice_agent_url=args.websocket_url
    )
    
    logger.info(f"🚀 Starting mock notification simulation: {args.scenario}")
    logger.info(f"📡 Voice agent URL: {generator.voice_agent_url}")
    
    try:
        if args.scenario == "single":
            await generator.simulate_single_order(
                coffee_type=args.coffee,
                delay_between_status=args.delay
            )
        
        elif args.scenario == "rush_period":
            await generator.simulate_rush_period(
                num_orders=args.orders,
                delay_between_orders=args.delay,
                delay_between_status=1.0
            )
        
        elif args.scenario == "mixed":
            await generator.simulate_mixed_coffee_types(delay=args.delay)
        
        elif args.scenario == "errors":
            await generator.simulate_error_scenarios()
        
        logger.info("🎉 Mock notification simulation completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Simulation interrupted by user")
    except Exception as e:
        logger.error(f"❌ Simulation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 