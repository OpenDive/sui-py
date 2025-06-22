"""
Event handlers for the Coffee Club Event Indexer.

This module exports all event handlers for processing different types of
blockchain events from the coffee club contract.
"""

import sys
from pathlib import Path

# Handle both direct script execution and module import
try:
    from cafe_handler import handle_cafe_events
    from order_handler import handle_order_events
except ImportError:
    try:
        from .cafe_handler import handle_cafe_events
        from .order_handler import handle_order_events
    except ImportError:
        # Add current directory to path for direct execution
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        from cafe_handler import handle_cafe_events
        from order_handler import handle_order_events

__all__ = [
    "handle_cafe_events",
    "handle_order_events"
] 