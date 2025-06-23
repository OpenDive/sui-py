#!/usr/bin/env python3
"""
Example script demonstrating how to use the MockNotificationGenerator.

This script shows how to import and use the mock notification system
for testing voice agent integration.
"""

import asyncio
import logging
from handlers import MockNotificationGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_mock_notifications():
    """Demonstrate various mock notification scenarios."""
    
    logger.info("🎭 Starting Mock Notification Demo")
    
    # Initialize the mock generator
    generator = MockNotificationGenerator()
    
    try:
        # 1. Single order demo
        logger.info("\n📋 Demo 1: Single Order Lifecycle")
        await generator.simulate_single_order(
            coffee_type="Espresso",
            delay_between_status=1.0
        )
        
        await asyncio.sleep(2)  # Pause between demos
        
        # # 2. Mixed coffee types demo
        # logger.info("\n🌈 Demo 2: Mixed Coffee Types")
        # await generator.simulate_mixed_coffee_types(delay=0.5)
        
        # await asyncio.sleep(2)  # Pause between demos
        
        # # 3. Mini rush period demo
        # logger.info("\n🏃 Demo 3: Mini Rush Period")
        # await generator.simulate_rush_period(
        #     num_orders=3,
        #     delay_between_orders=0.5,
        #     delay_between_status=0.8
        # )
        
        logger.info("\n🎉 Mock notification demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    print("🚀 Coffee Club Mock Notification Demo")
    print("This demo shows how the MockNotificationGenerator works.")
    print("Note: Voice agent may not be running, so expect connection warnings.")
    print()
    
    asyncio.run(demo_mock_notifications()) 