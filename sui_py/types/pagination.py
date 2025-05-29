"""
Pagination types for Sui API responses.

These types handle paginated responses from the Sui JSON-RPC API.
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class Page(Generic[T]):
    """
    Generic paginated response wrapper.
    
    This corresponds to the Page_for_* schemas in the Sui API.
    """
    data: List[T]
    has_next_page: bool
    next_cursor: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], item_parser=None) -> "Page[T]":
        """
        Create a Page from a dictionary response.
        
        Args:
            data: The raw API response dictionary
            item_parser: Optional function to parse individual items
            
        Returns:
            Page instance with parsed data
        """
        items = data.get("data", [])
        
        # If item_parser is provided, parse each item
        if item_parser:
            parsed_items = [item_parser(item) for item in items]
        else:
            parsed_items = items
        
        return cls(
            data=parsed_items,
            has_next_page=data.get("hasNextPage", False),
            next_cursor=data.get("nextCursor")
        )
    
    def __len__(self) -> int:
        """Return the number of items in this page."""
        return len(self.data)
    
    def __iter__(self):
        """Allow iteration over the data items."""
        return iter(self.data)
    
    def __getitem__(self, index):
        """Allow indexing into the data items."""
        return self.data[index]
    
    def is_empty(self) -> bool:
        """Check if this page contains no data."""
        return len(self.data) == 0 