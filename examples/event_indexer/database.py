"""
Database connection and session management for the SuiPy Event Indexer.

This module provides async database connectivity using SQLAlchemy 2.0
with support for SQLite and PostgreSQL.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import CONFIG
from .models import Base

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.engine: AsyncEngine = create_async_engine(
            CONFIG.database.url,
            echo=CONFIG.database.echo,
            future=True
        )
        
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self) -> None:
        """Create all database tables."""
        logger.info("Creating database tables...")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    
    async def drop_tables(self) -> None:
        """Drop all database tables."""
        logger.info("Dropping database tables...")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped successfully")
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        async with self.async_session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self) -> None:
        """Close the database connection."""
        await self.engine.dispose()
        logger.info("Database connection closed")


# Global database instance
database = Database()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function to get a database session."""
    async with database.get_session() as session:
        yield session 