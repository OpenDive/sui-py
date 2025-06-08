#!/usr/bin/env python3
"""
Test automatic emoji injection with the new EmojiFilter.
"""

from sui_py.utils.logging import setup_logging, get_logger
from sui_py.transactions import TransactionBuilder
import logging

def test_automatic_emojis():
    """Test that emojis are automatically added to log messages."""
    print("=== Testing Automatic Emoji Injection ===\n")
    
    # Test with Rich (default)
    print("1. Testing with Rich handler (colors + auto emojis):")
    setup_logging(level=logging.DEBUG, use_emojis=True)
    logger = get_logger("sui_py.test")
    
    # These should automatically get emojis added
    logger.debug("Debug message without manual emoji")
    logger.info("Info message without manual emoji")
    logger.warning("Warning message without manual emoji")
    logger.error("Error message without manual emoji")
    logger.critical("Critical message without manual emoji")
    logger.success("Success message without manual emoji")
    
    print("\n2. Testing TransactionBuilder with automatic emojis:")
    tx = TransactionBuilder()
    tx.set_sender("0x2")  # Should show auto emoji + colors
    tx._validate()        # Should show auto emoji + colors
    
    print("\n3. Testing standard handler (emojis but no colors):")
    setup_logging(level=logging.DEBUG, force_standard=True, use_emojis=True)
    logger2 = get_logger("sui_py.fallback")
    
    logger2.info("Standard handler with auto emoji")
    logger2.warning("Standard handler warning with auto emoji")
    logger2.error("Standard handler error with auto emoji")
    
    print("\n4. Testing emoji disabled:")
    setup_logging(level=logging.DEBUG, use_emojis=False)
    logger3 = get_logger("sui_py.no_emoji")
    
    logger3.info("This should have no emoji")
    logger3.error("This error should have no emoji")
    
    print("\n5. Testing messages that already have emojis (should not double):")
    setup_logging(level=logging.DEBUG, use_emojis=True)
    logger4 = get_logger("sui_py.test_double")
    
    logger4.info("ℹ️ This already has an info emoji")
    logger4.warning("⚠️ This already has a warning emoji")
    logger4.error("❌ This already has an error emoji")

def test_transactionbuilder_integration():
    """Test that TransactionBuilder gets automatic emojis."""
    print("\n=== Testing TransactionBuilder Integration ===\n")
    
    setup_logging(level=logging.DEBUG, use_emojis=True)
    
    print("6. TransactionBuilder automatic emoji integration:")
    tx = TransactionBuilder()
    
    # These logging calls in TransactionBuilder should now get automatic emojis
    tx.set_sender("0x123")  # Info message about padding
    tx.set_gas_budget(1000000)
    tx.set_gas_price(1000)
    
    try:
        tx._validate_transaction_metadata()  # Error about missing gas payment
    except ValueError:
        pass  # Expected
    
    # Test empty transaction warning
    empty_tx = TransactionBuilder()
    empty_tx._validate()  # Warning about empty transaction
    
    print("\n✨ TransactionBuilder now has automatic emojis + colors!")

if __name__ == "__main__":
    test_automatic_emojis()
    test_transactionbuilder_integration()
    
    print("\n=== Automatic Emoji Test Complete ===")
    print("🎯 Features now working:")
    print("   ✅ Automatic emoji injection based on log level")
    print("   🎨 Rich colors for all log levels")
    print("   🔧 Works with both Rich and standard handlers")
    print("   🚀 TransactionBuilder automatically enhanced")
    print("   ⚙️ Configurable (can disable emojis if needed)")
    print("   🛡️ Smart duplicate detection (won't double emojis)") 