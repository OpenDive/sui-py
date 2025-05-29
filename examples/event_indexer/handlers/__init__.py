"""
Event handlers for the SuiPy Event Indexer.

This package contains handlers for processing different types of events
from the Sui blockchain using typed SuiEvent objects.
"""

from .escrow_handler import handle_escrow_objects
from .locked_handler import handle_lock_objects

__all__ = [
    "handle_escrow_objects",
    "handle_lock_objects"
] 