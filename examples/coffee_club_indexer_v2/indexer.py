#!/usr/bin/env python3
"""
Coffee Club Event Indexer

A comprehensive event indexer for the Coffee Club smart contract that processes
cafe creation and coffee order events, integrates with coffee machines, and
maintains a persistent database of all activities.

This indexer demonstrates real-time event processing, external system integration,
and robust error handling in a production-ready SuiPy application.
"""

# Handle imports when running from within SDK source tree
import sys
import os
# Add the SDK root (sui-py directory) to Python path
sdk_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if sdk_root not in sys.path:
    sys.path.insert(0, sdk_root)

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Add the current directory to Python path for relative imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Auto-setup integration - run BEFORE importing Prisma
try:
    from database_setup import setup_with_fallback, ensure_prisma_client
except ImportError:
    from .database_setup import setup_with_fallback, ensure_prisma_client

# Ensure Prisma client is ready before importing
print("Checking database client setup...")
if not ensure_prisma_client():
    print("❌ Failed to set up database client. Please run 'python setup.py' manually.")
    sys.exit(1)

# Now safe to import Prisma
from prisma import Prisma
from prisma.models import Cursor

from sui_py import SuiClient, SuiEvent, EventFilter, Page
from sui_py.exceptions import SuiRPCError, SuiValidationError

try:
    from config import CONFIG
    from handlers import handle_cafe_events, handle_order_events
except ImportError:
    from .config import CONFIG
    from .handlers import handle_cafe_events, handle_order_events

logger = logging.getLogger(__name__)


@dataclass
class EventExecutionResult:
    """Result of executing an event job."""
    cursor: Optional[str]
    has_next_page: bool


@dataclass
class EventTracker:
    """Configuration for tracking a specific event type."""
    # The event type with format `package::module::EventName`
    type: str
    # Event filter for querying
    filter: Dict[str, Any]
    # Callback function to handle events
    callback: Callable[[List[SuiEvent], str, Prisma], Any]


class CoffeeClubIndexer:
    """Main coffee club event indexer class."""
    
    def __init__(self):
        """Initialize the coffee club event indexer."""
        self.client: Optional[SuiClient] = None
        self.db: Optional[Prisma] = None
        self.running = False
        self.limit = CONFIG.batch_size
        
        # Define events to track for coffee club
        package_id = CONFIG.coffee_club_contract.package_id
        self.events_to_track: List[EventTracker] = [
            EventTracker(
                type=f"{package_id}::suihub_cafe::CafeCreated",
                filter=EventFilter.by_event_type(f"{package_id}::suihub_cafe::CafeCreated"),
                callback=handle_cafe_events
            ),
            EventTracker(
                type=f"{package_id}::suihub_cafe::CoffeeOrderCreated", 
                filter=EventFilter.by_event_type(f"{package_id}::suihub_cafe::CoffeeOrderCreated"),
                callback=handle_order_events
            ),
            EventTracker(
                type=f"{package_id}::suihub_cafe::CoffeeOrderUpdated",
                filter=EventFilter.by_event_type(f"{package_id}::suihub_cafe::CoffeeOrderUpdated"),
                callback=handle_order_events
            )
        ]
    
    async def start(self) -> None:
        """Start the coffee club event indexer."""
        logger.info("Starting Coffee Club Event Indexer...")
        
        # Ensure Prisma client is ready
        if not ensure_prisma_client():
            logger.error("Failed to set up database client. Cannot start indexer.")
            return
        
        logger.info(f"Network: {CONFIG.network}")
        logger.info(f"RPC URL: {CONFIG.rpc_url}")
        logger.info(f"Coffee Club Contract: {CONFIG.coffee_club_contract.package_id}")
        logger.info(f"Database URL: {CONFIG.database_url}")
        logger.info(f"Polling Interval: {CONFIG.polling_interval_ms}ms")
        logger.info(f"Coffee Machine Enabled: {CONFIG.coffee_machine.enabled}")
        if CONFIG.coffee_machine.enabled:
            logger.info(f"Coffee Machine MAC: {CONFIG.coffee_machine.mac_address}")
        
        # Initialize Prisma database
        self.db = Prisma()
        await self.db.connect()
        logger.info("Connected to database")
        
        # Initialize Sui client
        self.client = SuiClient(CONFIG.rpc_url)
        await self.client.connect()
        logger.info("Connected to Sui network")
        
        # Start event listeners
        self.running = True
        await self._setup_listeners()
    
    async def stop(self) -> None:
        """Stop the coffee club event indexer."""
        logger.info("Stopping Coffee Club Event Indexer...")
        self.running = False
        
        if self.client:
            await self.client.close()
        
        if self.db:
            await self.db.disconnect()
        
        logger.info("Coffee club event indexer stopped")
    
    async def _setup_listeners(self) -> None:
        """Set up all event listeners."""
        logger.info(f"Setting up listeners for {len(self.events_to_track)} event types")
        
        # Start a task for each event tracker
        tasks = []
        for event_tracker in self.events_to_track:
            cursor = await self._get_latest_cursor(event_tracker)
            task = asyncio.create_task(
                self._run_event_job(event_tracker, cursor),
                name=f"event_job_{event_tracker.type}"
            )
            tasks.append(task)
        
        # Wait for all tasks to complete (they run indefinitely)
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Event listener tasks cancelled")
            for task in tasks:
                if not task.done():
                    task.cancel()
    
    async def _run_event_job(self, tracker: EventTracker, cursor: Optional[str]) -> None:
        """
        Run an event job continuously.
        
        Args:
            tracker: Event tracker configuration
            cursor: Starting cursor position
        """
        logger.info(f"Starting event job for {tracker.type}")
        current_cursor = cursor
        retry_count = 0
        
        while self.running:
            try:
                result = await self._execute_event_job(tracker, current_cursor)
                current_cursor = result.cursor
                retry_count = 0  # Reset retry count on success
                
                # Determine sleep interval
                if result.has_next_page:
                    # No delay if there are more pages to process
                    sleep_ms = 0
                else:
                    # Use polling interval if no more pages
                    sleep_ms = CONFIG.polling_interval_ms
                
                if sleep_ms > 0:
                    await asyncio.sleep(sleep_ms / 1000.0)
                    
            except Exception as e:
                retry_count += 1
                logger.error(f"Error in event job {tracker.type} (attempt {retry_count}): {e}")
                
                if retry_count >= CONFIG.max_retries:
                    logger.error(f"Max retries exceeded for {tracker.type}, stopping job")
                    break
                
                # Use error retry interval for transient errors
                sleep_ms = CONFIG.error_retry_interval_ms
                logger.info(f"Retrying {tracker.type} in {sleep_ms}ms...")
                await asyncio.sleep(sleep_ms / 1000.0)
        
        logger.info(f"Event job for {tracker.type} stopped")
    
    async def _execute_event_job(
        self, 
        tracker: EventTracker, 
        cursor: Optional[str]
    ) -> EventExecutionResult:
        """
        Execute a single event job iteration.
        
        Args:
            tracker: Event tracker configuration
            cursor: Current cursor position
            
        Returns:
            Result containing new cursor and pagination info
        """
        try:
            logger.debug(f"Querying events for {tracker.type} with cursor: {cursor}")
            
            # Query events from the blockchain
            result = await self.client.extended_api.query_events(
                query=tracker.filter,
                cursor=cursor,
                limit=self.limit,
                descending_order=False
            )
            
            events = result.data if result else []
            has_next_page = result.has_next_page if result else False
            next_cursor = result.next_cursor if result else None
            
            logger.info(f"Retrieved {len(events)} events for {tracker.type}")
            
            if events:
                logger.debug(f"First event in batch: {events[0].type}")
                
                # Process events using the appropriate handler
                await tracker.callback(events, tracker.type, self.db)
                
                # Save cursor if we have a next cursor
                if next_cursor and events:
                    await self._save_latest_cursor(tracker, next_cursor)
                    return EventExecutionResult(
                        cursor=next_cursor,
                        has_next_page=has_next_page
                    )
            
            return EventExecutionResult(
                cursor=cursor,
                has_next_page=has_next_page
            )
            
        except (SuiRPCError, SuiValidationError) as e:
            logger.error(f"Sui error processing events for {tracker.type}: {e}")
            if self._is_transient_error(e):
                logger.info(f"Transient error detected for {tracker.type}, will retry")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing events for {tracker.type}: {e}")
            raise
    
    def _is_transient_error(self, error: Exception) -> bool:
        """Check if an error is transient and can be retried."""
        error_msg = str(error).lower()
        transient_indicators = [
            'network error',
            'timeout',
            'rate limit',
            'too many requests',
            'connection',
            'temporary'
        ]
        return any(indicator in error_msg for indicator in transient_indicators)
    
    async def _get_latest_cursor(self, tracker: EventTracker) -> Optional[str]:
        """
        Get the latest cursor for an event tracker.
        
        Args:
            tracker: Event tracker configuration
            
        Returns:
            Latest cursor string or None if not found
        """
        try:
            logger.debug(f"Retrieving latest cursor for {tracker.type}")
            cursor = await self.db.cursor.find_unique(
                where={"id": tracker.type}
            )
            
            if cursor:
                # Construct cursor from eventSeq and txDigest
                cursor_str = f"{cursor.eventSeq}:{cursor.txDigest}"
                logger.debug(f"Retrieved cursor for {tracker.type}: {cursor_str}")
                return cursor_str
            else:
                logger.debug(f"No cursor found for {tracker.type}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving cursor for {tracker.type}: {e}")
            return None
    
    async def _save_latest_cursor(
        self, 
        tracker: EventTracker, 
        cursor: str
    ) -> None:
        """
        Save the latest cursor for an event tracker.
        
        Args:
            tracker: Event tracker configuration
            cursor: Cursor string to save
        """
        try:
            # Parse cursor format "eventSeq:txDigest"
            if ":" in cursor:
                event_seq, tx_digest = cursor.split(":", 1)
            else:
                # Fallback format
                event_seq = cursor
                tx_digest = cursor
            
            data = {
                "eventSeq": event_seq,
                "txDigest": tx_digest,
            }
            
            logger.debug(f"Saving cursor for {tracker.type}: {data}")
            
            await self.db.cursor.upsert(
                where={"id": tracker.type},
                data={
                    "create": {"id": tracker.type, **data},
                    "update": data
                }
            )
            
        except Exception as e:
            logger.error(f"Error saving cursor for {tracker.type}: {e}")
            raise


async def main():
    """Main entry point for the coffee club indexer."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start the indexer
    indexer = CoffeeClubIndexer()
    
    try:
        await indexer.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Indexer failed: {e}")
        raise
    finally:
        await indexer.stop()


if __name__ == "__main__":
    asyncio.run(main()) 