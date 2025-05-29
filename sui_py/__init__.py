"""
SuiPy - A lightweight, high-performance Python SDK for the Sui blockchain.

Async-first design for optimal performance with I/O-bound blockchain operations.
"""

__version__ = "0.1.0"
__author__ = "SuiPy Team"

from .client import SuiClient
from .exceptions import SuiError, SuiRPCError, SuiValidationError

__all__ = [
    "SuiClient",
    "SuiError", 
    "SuiRPCError",
    "SuiValidationError",
] 