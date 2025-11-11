"""
Custom exceptions for SuiPy SDK.

Following Pythonic design principles with multiple inheritance from built-in
exception types for better integration with standard Python error handling.
"""

from typing import Any, Optional


class SuiError(Exception):
    """Base exception for all Sui-related errors."""
    pass


class SuiRPCError(SuiError):
    """Exception raised for JSON-RPC errors from Sui nodes."""
    
    def __init__(
        self, 
        message: str, 
        code: Optional[int] = None, 
        data: Optional[Any] = None,
        method: Optional[str] = None
    ):
        super().__init__(message)
        self.code = code
        self.data = data
        self.method = method  # RPC method that failed
        
    def __str__(self) -> str:
        if self.code:
            method_info = f" ({self.method})" if self.method else ""
            return f"RPC Error {self.code}{method_info}: {super().__str__()}"
        return super().__str__()


class SuiValidationError(SuiError, ValueError):
    """
    Exception raised for invalid input parameters.
    
    Inherits from both SuiError and ValueError for Pythonic error handling.
    Can be caught as either exception type.
    """
    pass


class SuiNetworkError(SuiError, ConnectionError):
    """
    Exception raised for network-related errors.
    
    Inherits from both SuiError and ConnectionError for standard
    Python network error handling patterns.
    """
    pass


class SuiTimeoutError(SuiError, TimeoutError):
    """
    Exception raised when requests timeout.
    
    Inherits from both SuiError and TimeoutError for standard
    Python timeout handling patterns.
    """
    pass 