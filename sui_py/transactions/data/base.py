"""
Base imports and types for transaction data structures.
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import List, Optional

from ...bcs import Serializer, Deserializer, Serializable, Deserializable
from ...types import SuiAddress, ObjectRef
from ..ptb import ProgrammableTransactionBlock

class TransactionType(IntEnum):
    """Transaction type enumeration."""
    V1 = 0
