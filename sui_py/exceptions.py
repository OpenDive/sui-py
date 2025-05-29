"""
Custom exceptions for SuiPy SDK.
"""

from typing import Any, Dict, Optional


class SuiError(Exception):
    """Base exception for all Sui-related errors."""
    pass


class SuiRPCError(SuiError):
    """Exception raised for JSON-RPC errors from Sui nodes."""
    
    def __init__(self, message: str, code: Optional[int] = None, data: Optional[Any] = None):
        super().__init__(message)
        self.code = code
        self.data = data
        
    def __str__(self) -> str:
        if self.code:
            return f"RPC Error {self.code}: {super().__str__()}"
        return super().__str__()


class SuiValidationError(SuiError):
    """Exception raised for invalid input parameters."""
    pass


class SuiNetworkError(SuiError):
    """Exception raised for network-related errors."""
    pass


class SuiTimeoutError(SuiError):
    """Exception raised when requests timeout."""
    pass 