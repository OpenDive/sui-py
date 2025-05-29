"""
Database models for the SuiPy Event Indexer.

This module defines the SQLAlchemy models for storing indexed event data,
including escrow objects, locked objects, and cursor tracking.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models."""
    pass


class Cursor(Base):
    """
    Tracks the last processed event cursor for each event type.
    
    This allows the indexer to resume from where it left off after restarts.
    """
    __tablename__ = "cursors"
    
    # Event type identifier (e.g., "package::module")
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # Event cursor information
    event_seq: Mapped[str] = mapped_column(String(50), nullable=False)
    tx_digest: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<Cursor(id='{self.id}', tx_digest='{self.tx_digest}', event_seq='{self.event_seq}')>"


class Escrow(Base):
    """
    Represents an escrow object from the swap contract.
    
    Tracks the lifecycle of escrow objects including creation, swapping, and cancellation.
    """
    __tablename__ = "escrows"
    
    # Primary identifier
    object_id: Mapped[str] = mapped_column(String(66), primary_key=True)  # 0x + 64 hex chars
    
    # Escrow details (set on creation)
    sender: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    recipient: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    key_id: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    item_id: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    
    # Status flags
    swapped: Mapped[bool] = mapped_column(Boolean, default=False)
    cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        status = "active"
        if self.cancelled:
            status = "cancelled"
        elif self.swapped:
            status = "swapped"
        
        return f"<Escrow(object_id='{self.object_id}', status='{status}', sender='{self.sender}')>"


class Locked(Base):
    """
    Represents a locked object from the swap contract.
    
    Tracks the lifecycle of locked objects including creation and destruction.
    """
    __tablename__ = "locked"
    
    # Primary identifier
    object_id: Mapped[str] = mapped_column(String(66), primary_key=True)  # 0x + 64 hex chars
    
    # Lock details (set on creation)
    creator: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    key_id: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    item_id: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    
    # Status flags
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        status = "active" if not self.deleted else "deleted"
        return f"<Locked(object_id='{self.object_id}', status='{status}', creator='{self.creator}')>" 