"""
Coffee machine integration module for the Coffee Club Event Indexer.

This module provides integration with physical coffee machines,
currently supporting DeLonghi controllers via Python subprocess calls.
"""

from .controller import CoffeeMachineController

__all__ = ["CoffeeMachineController"] 