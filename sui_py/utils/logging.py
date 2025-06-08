"""
Logging utilities for SuiPy SDK with Rich integration.

Provides automatic coloring, emoji insertion, and proper terminal detection
while respecting standard environment variables like NO_COLOR.
"""

import logging
import os
import sys
from typing import Optional

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.theme import Theme
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Custom theme for SuiPy - only add our custom SUCCESS level
SUI_THEME = Theme({
    "logging.level.success": "bold green",
})


class EmojiFilter(logging.Filter):
    """
    Logging filter that automatically adds emojis to log messages based on level.
    
    This filter works with any handler (Rich or standard) and adds emojis
    consistently across the entire logging system.
    """
    
    # Emoji mapping for different log levels
    EMOJIS = {
        logging.DEBUG: "🔍 ",
        logging.INFO: "ℹ️ ",
        logging.WARNING: "⚠️ ",
        logging.ERROR: "❌ ",
        logging.CRITICAL: "💥 ",
    }
    
    # Custom level for success messages
    SUCCESS_LEVEL = 25
    
    def __init__(self, use_emojis: bool = True):
        super().__init__()
        self.use_emojis = use_emojis
        # Add success emoji
        self.EMOJIS[self.SUCCESS_LEVEL] = "✅ "
    
    def filter(self, record):
        """
        Add emoji to log message if enabled and not already present.
        
        Args:
            record: LogRecord to potentially modify
            
        Returns:
            True to allow the record through (always)
        """
        if self.use_emojis:
            emoji = self.EMOJIS.get(record.levelno, "")
            if emoji:
                message = record.getMessage()
                # Only add emoji if not already present
                if not message.startswith(emoji.strip()):
                    record.msg = f"{emoji}{record.msg}"
        
        return True  # Always allow the record through


class SuiFormatter(logging.Formatter):
    """
    Custom formatter for standard handlers (when Rich is not available).
    
    Note: Emoji injection is now handled by EmojiFilter, so this formatter
    only handles basic formatting.
    """
    
    # Custom level for success messages
    SUCCESS_LEVEL = 25
    
    def __init__(self):
        super().__init__("%(levelname)s %(message)s")


def _should_use_colors() -> bool:
    """
    Determine if colors should be used based on environment and terminal capabilities.
    
    Respects standard environment variables:
    - NO_COLOR: Disable colors when set (any value)
    - FORCE_COLOR: Force colors when set (any value)  
    - SUI_PY_NO_COLOR: Disable colors specifically for sui-py
    - TERM: Terminal type detection
    """
    # Check for explicit disable flags
    if os.environ.get("NO_COLOR"):
        return False
    
    if os.environ.get("SUI_PY_NO_COLOR"):
        return False
    
    # Check for explicit enable flag
    if os.environ.get("FORCE_COLOR"):
        return True
    
    # Check if output is being redirected
    if not sys.stdout.isatty():
        return False
    
    # Check terminal type
    term = os.environ.get("TERM", "").lower()
    if term in ("dumb", ""):
        return False
    
    return True


def _create_rich_handler() -> Optional[logging.Handler]:
    """Create a Rich handler if Rich is available and colors are enabled."""
    if not RICH_AVAILABLE:
        return None
    
    if not _should_use_colors():
        return None
    
    try:
        console = Console(
            theme=SUI_THEME,
            force_terminal=True,  # Force terminal detection
            no_color=bool(os.environ.get("NO_COLOR")),
            color_system="truecolor",  # Explicitly set color system
        )
        
        handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
            show_time=False,
            show_path=False,
            markup=True,
        )
        
        # Don't set a custom formatter - let Rich handle the formatting and colors
        return handler
    except Exception:
        # Fallback if Rich setup fails
        return None


def _create_standard_handler() -> logging.Handler:
    """Create a standard StreamHandler with our custom formatter."""
    handler = logging.StreamHandler(sys.stdout)
    
    formatter = SuiFormatter()
    handler.setFormatter(formatter)
    
    return handler


def setup_logging(level: int = logging.INFO, force_standard: bool = False, use_emojis: bool = True) -> None:
    """
    Set up logging for the SuiPy SDK.
    
    Args:
        level: Logging level (default: INFO)
        force_standard: If True, use standard handler even if Rich is available
        use_emojis: If True, automatically add emojis to log messages based on level
    """
    # Add custom SUCCESS level
    logging.addLevelName(EmojiFilter.SUCCESS_LEVEL, "SUCCESS")
    
    # Get the root sui_py logger
    logger = logging.getLogger("sui_py")
    
    # Clear any existing handlers and filters
    logger.handlers.clear()
    logger.filters.clear()
    logger.propagate = False
    
    # Create emoji filter
    emoji_filter = EmojiFilter(use_emojis=use_emojis)
    logger.addFilter(emoji_filter)
    
    # Create appropriate handler
    if not force_standard:
        handler = _create_rich_handler()
        if handler is None:
            handler = _create_standard_handler()
    else:
        handler = _create_standard_handler()
    
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.setLevel(level)


def get_logger(name: str = "sui_py") -> logging.Logger:
    """
    Get a logger for the SuiPy SDK.
    
    Args:
        name: Logger name (default: "sui_py")
        
    Returns:
        Configured logger instance
    """
    # Ensure logging is set up for the root sui_py logger
    root_logger = logging.getLogger("sui_py")
    if not root_logger.handlers:
        setup_logging()
    
    # Get the requested logger
    logger = logging.getLogger(name)
    
    # For child loggers, copy the emoji filter from root and ensure propagation
    if name != "sui_py" and name.startswith("sui_py."):
        logger.propagate = True  # Allow propagation to parent
        
        # Add emoji filter to child logger if root has one
        if root_logger.filters:
            # Check if child already has an EmojiFilter
            has_emoji_filter = any(hasattr(f, 'EMOJIS') for f in logger.filters)
            if not has_emoji_filter:
                for filter_obj in root_logger.filters:
                    if hasattr(filter_obj, 'EMOJIS'):  # It's our EmojiFilter
                        logger.addFilter(filter_obj)
    
    return logger


# Convenience function to add success logging method
def _log_success(self, message, *args, **kwargs):
    """Log a success message."""
    if self.isEnabledFor(EmojiFilter.SUCCESS_LEVEL):
        self._log(EmojiFilter.SUCCESS_LEVEL, message, args, **kwargs)


# Monkey patch the success method onto Logger
logging.Logger.success = _log_success


# Auto-setup logging when module is imported
if not logging.getLogger("sui_py").handlers:
    setup_logging() 