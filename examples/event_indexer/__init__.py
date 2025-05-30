"""
SuiPy Event Indexer

A real-time event indexer for the Sui blockchain built with the SuiPy SDK.
Demonstrates how to use typed Extended API schemas with Prisma Client Python
for production-grade blockchain data indexing.

Features:
- Real-time event processing using typed SuiEvent objects
- Automatic cursor tracking and resumption
- Database persistence with Prisma Client Python
- Configurable retry logic and error handling
- Support for SQLite and PostgreSQL
- Modular event handler architecture
- Schema-first database design
- Auto-setup with zero configuration
"""

# Auto-setup integration - ensure Prisma client is ready
try:
    from .setup import ensure_prisma_client
    
    # Only run auto-setup if we're being imported as a module
    # (not during setup.py execution)
    import sys
    if not any('setup.py' in arg for arg in sys.argv):
        if not ensure_prisma_client():
            print("⚠️  Database client setup incomplete.")
            print("   Run 'python setup.py' to complete setup manually.")
except ImportError:
    # setup.py might not be available in some contexts
    pass

from .config import CONFIG

# Import main components with graceful error handling
try:
    from .indexer import EventIndexer, main
    __all__ = ["CONFIG", "EventIndexer", "main"]
except ImportError as e:
    print(f"⚠️  Some components not available: {e}")
    print("   This usually means the database client needs to be set up.")
    print("   Run 'python setup.py' to complete setup.")
    __all__ = ["CONFIG"]

__version__ = "1.0.0" 