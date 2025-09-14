"""
Test data package for SuiPy SDK tests.

Contains sample JSON responses from Sui RPC API for testing and validation.
Organized by API type: write_api, read_api, move_utils.

This data is used by unit tests to validate schema parsing and response handling.
"""

from .loader import load_json, load_all_samples

__all__ = ["load_json", "load_all_samples"]
