"""
Event handlers for the SuiPy Event Indexer.

This module exports all event handlers for processing different types of
blockchain events from the swap contract.
"""

import sys
from pathlib import Path

# Handle both direct script execution and module import
try:
    from escrow_handler import handle_escrow_objects
    from locked_handler import handle_lock_objects
except ImportError:
    try:
        from .escrow_handler import handle_escrow_objects
        from .locked_handler import handle_lock_objects
    except ImportError:
        # Add current directory to path for direct execution
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        from escrow_handler import handle_escrow_objects
        from locked_handler import handle_lock_objects

__all__ = [
    "handle_escrow_objects",
    "handle_lock_objects"
] 