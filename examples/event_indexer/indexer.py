"""
Main event indexer for the SuiPy Event Indexer.

This module implements the core event indexing logic, polling the Sui blockchain
for events and processing them using typed SuiEvent objects and handlers.
"""

import asyncio
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Add the current directory to Python path for relative imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Auto-setup integration - run BEFORE importing Prisma
try:
    from setup import setup_with_fallback, ensure_prisma_client
except ImportError:
    from .setup import setup_with_fallback, ensure_prisma_client

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
    from handlers import handle_escrow_objects, handle_lock_objects
except ImportError:
    from .config import CONFIG
    from .handlers import handle_escrow_objects, handle_lock_objects

logger = logging.getLogger(__name__)


@dataclass
class EventExecutionResult:
    """Result of executing an event job."""
    cursor: Optional[str]
    has_next_page: bool


@dataclass
class EventTracker:
    """Configuration for tracking a specific event type."""
    # The module that defines the type, with format `package::module`
    type: str
    # Event filter for querying
    filter: Dict[str, Any]
    # Callback function to handle events
    callback: Callable[[List[SuiEvent], str, Prisma], Any]


class EventIndexer:
    """Main event indexer class."""
    
    def __init__(self):
        """Initialize the event indexer."""
        self.client: Optional[SuiClient] = None
        self.db: Optional[Prisma] = None
        self.running = False
        
        # Define events to track
        self.events_to_track: List[EventTracker] = [
            EventTracker(
                type=f"{CONFIG.swap_contract.package_id}::lock",
                filter=EventFilter.by_module(CONFIG.swap_contract.package_id, "lock"),
                callback=handle_lock_objects
            ),
            EventTracker(
                type=f"{CONFIG.swap_contract.package_id}::shared",
                filter=EventFilter.by_module(CONFIG.swap_contract.package_id, "shared"),
                callback=handle_escrow_objects
            )
        ]
    
    async def start(self) -> None:
        """Start the event indexer."""
        logger.info("Starting SuiPy Event Indexer...")
        
        # Ensure Prisma client is ready
        if not ensure_prisma_client():
            logger.error("Failed to set up database client. Cannot start indexer.")
            return
        
        logger.info(f"Network: {CONFIG.network}")
        logger.info(f"RPC URL: {CONFIG.rpc_url}")
        logger.info(f"Swap Contract: {CONFIG.swap_contract.package_id}")
        logger.info(f"Database URL: {CONFIG.database_url}")
        logger.info(f"Polling Interval: {CONFIG.polling_interval_ms}ms")
        
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
        """Stop the event indexer."""
        logger.info("Stopping SuiPy Event Indexer...")
        self.running = False
        
        if self.client:
            await self.client.close()
        
        if self.db:
            await self.db.disconnect()
        
        logger.info("Event indexer stopped")
    
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
                
                # Exponential backoff
                sleep_ms = CONFIG.retry_delay_ms * (2 ** (retry_count - 1))
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
            EventExecutionResult with new cursor and pagination info
        """
        try:
            logger.debug(f"Querying events for {tracker.type} from cursor {cursor}")
            
            # Query events from the chain using typed Extended API
            events_page: Page[SuiEvent] = await self.client.extended_api.query_events(
                query=tracker.filter,
                cursor=cursor,
                limit=CONFIG.batch_size,
                descending_order=False  # Process in ascending order
            )
            
            logger.debug(f"Retrieved {len(events_page)} events for {tracker.type}")
            
            # Process events if any were found
            if len(events_page) > 0:
                # Handle the events using the tracker's callback
                await tracker.callback(list(events_page), tracker.type, self.db)
                
                # Save the latest cursor if we have a next cursor
                if events_page.next_cursor:
                    await self._save_latest_cursor(tracker, events_page.next_cursor)
                
                return EventExecutionResult(
                    cursor=events_page.next_cursor,
                    has_next_page=events_page.has_next_page
                )
            else:
                logger.debug(f"No new events for {tracker.type}")
                
        except SuiRPCError as e:
            logger.error(f"RPC error querying events for {tracker.type}: {e}")
            raise
        except SuiValidationError as e:
            logger.error(f"Validation error for {tracker.type}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing events for {tracker.type}: {e}")
            raise
        
        # Return current cursor with no next page
        return EventExecutionResult(
            cursor=cursor,
            has_next_page=False
        )
    
    async def _get_latest_cursor(self, tracker: EventTracker) -> Optional[str]:
        """
        Get the latest cursor for an event tracker from the database.
        
        Args:
            tracker: Event tracker configuration
            
        Returns:
            Latest cursor string or None if not found
        """
        cursor_record = await self.db.cursor.find_unique(
            where={"id": tracker.type}
        )
        
        if cursor_record:
            # Reconstruct cursor from stored components
            cursor = {
                "txDigest": cursor_record.txDigest,
                "eventSeq": cursor_record.eventSeq
            }
            logger.info(f"Resuming {tracker.type} from cursor: {cursor}")
            return cursor
        else:
            logger.info(f"No previous cursor found for {tracker.type}, starting from beginning")
            return None
    
    async def _save_latest_cursor(
        self, 
        tracker: EventTracker, 
        cursor: Any
    ) -> None:
        """
        Save the latest cursor for an event tracker to the database.
        
        Args:
            tracker: Event tracker configuration
            cursor: Cursor object from the API response
        """
        if not cursor:
            return
        
        # Extract cursor components
        if isinstance(cursor, dict):
            tx_digest = cursor.get("txDigest")
            event_seq = cursor.get("eventSeq")
        else:
            # Handle string cursor or other formats
            logger.warning(f"Unexpected cursor format for {tracker.type}: {cursor}")
            return
        
        if not tx_digest or not event_seq:
            logger.warning(f"Invalid cursor data for {tracker.type}: {cursor}")
            return
        
        # Upsert cursor record using Prisma
        try:
            await self.db.cursor.upsert(
                where={"id": tracker.type},
                data={
                    "txDigest": tx_digest,
                    "eventSeq": event_seq
                },
                create={
                    "id": tracker.type,
                    "txDigest": tx_digest,
                    "eventSeq": event_seq
                }
            )
            logger.debug(f"Saved cursor for {tracker.type}: {tx_digest}:{event_seq}")
        except Exception as e:
            logger.error(f"Failed to save cursor for {tracker.type}: {e}")
            raise


async def main():
    """Main entry point for the event indexer."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start indexer
    indexer = EventIndexer()
    
    try:
        await indexer.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        await indexer.stop()


if __name__ == "__main__":
    asyncio.run(main()) 