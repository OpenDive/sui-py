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


class SuiFormatter(logging.Formatter):
    """
    Custom formatter that adds emojis for standard handlers.
    Rich handlers don't use this formatter.
    """
    
    # Emoji mapping for different log levels
    EMOJIS = {
        logging.DEBUG: "🔍",
        logging.INFO: "ℹ️ ",
        logging.WARNING: "⚠️ ",
        logging.ERROR: "❌",
        logging.CRITICAL: "💥",
    }
    
    # Custom level for success messages
    SUCCESS_LEVEL = 25
    
    def __init__(self, use_emojis: bool = True):
        super().__init__("%(levelname)s %(message)s")
        self.use_emojis = use_emojis
        # Add success emoji
        self.EMOJIS[self.SUCCESS_LEVEL] = "✅"
    
    def format(self, record):
        # Add emoji to message if enabled and not already present
        if self.use_emojis:
            emoji = self.EMOJIS.get(record.levelno, "")
            if emoji and not record.getMessage().startswith(emoji):
                record.msg = f"{emoji} {record.msg}"
        
        return super().format(record)


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
    
    formatter = SuiFormatter(use_emojis=True)
    handler.setFormatter(formatter)
    
    return handler


def setup_logging(level: int = logging.INFO, force_standard: bool = False) -> None:
    """
    Set up logging for the SuiPy SDK.
    
    Args:
        level: Logging level (default: INFO)
        force_standard: If True, use standard handler even if Rich is available
    """
    # Add custom SUCCESS level
    logging.addLevelName(SuiFormatter.SUCCESS_LEVEL, "SUCCESS")
    
    # Get the root sui_py logger
    logger = logging.getLogger("sui_py")
    
    # Clear any existing handlers
    logger.handlers.clear()
    logger.propagate = False
    
    # Create appropriate handler
    if not force_standard:
        handler = _create_rich_handler()
        if handler is None:
            handler = _create_standard_handler()
        else:
            # Rich handler doesn't need custom formatter
            handler.setLevel(level)
            logger.addHandler(handler)
            logger.setLevel(level)
            return
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
    # Ensure logging is set up
    logger = logging.getLogger(name)
    if not logger.handlers:
        setup_logging()
    
    return logger


# Convenience function to add success logging method
def _log_success(self, message, *args, **kwargs):
    """Log a success message."""
    if self.isEnabledFor(SuiFormatter.SUCCESS_LEVEL):
        # Add level to extra for emoji detection
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra']['level'] = SuiFormatter.SUCCESS_LEVEL
        self._log(SuiFormatter.SUCCESS_LEVEL, message, args, **kwargs)


# Monkey patch the success method onto Logger
logging.Logger.success = _log_success


# Auto-setup logging when module is imported
if not logging.getLogger("sui_py").handlers:
    setup_logging() 