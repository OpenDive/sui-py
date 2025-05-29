"""
SuiPy Event Indexer

A real-time event indexer for the Sui blockchain built with the SuiPy SDK.
Demonstrates how to use typed Extended API schemas for production-grade
blockchain data indexing.

Features:
- Real-time event processing using typed SuiEvent objects
- Automatic cursor tracking and resumption
- Database persistence with SQLAlchemy 2.0
- Configurable retry logic and error handling
- Support for SQLite and PostgreSQL
- Modular event handler architecture
"""

from .config import CONFIG
from .indexer import EventIndexer, main
from .models import Base, Cursor, Escrow, Locked
from .database import database

__version__ = "1.0.0"

__all__ = [
    "CONFIG",
    "EventIndexer", 
    "main",
    "Base",
    "Cursor",
    "Escrow", 
    "Locked",
    "database"
] 