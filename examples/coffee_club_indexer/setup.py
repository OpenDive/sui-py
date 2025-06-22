"""
Setup utility for the Coffee Club Event Indexer.

This module provides auto-setup functionality for the coffee club indexer,
including Prisma client generation and database initialization.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_command(cmd: str, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """
    Run a shell command and return the result.
    
    Args:
        cmd: Command to run
        cwd: Working directory for the command
        
    Returns:
        CompletedProcess result
        
    Raises:
        subprocess.CalledProcessError: If command fails
    """
    logger.info(f"Running: {cmd}")
    if cwd:
        logger.debug(f"Working directory: {cwd}")
    
    return subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True
    )


def ensure_prisma_client() -> bool:
    """
    Ensure the Prisma client is generated and ready to use.
    
    Returns:
        True if client is ready, False otherwise
    """
    try:
        # Try to import Prisma client
        from prisma import Prisma
        logger.info("✅ Prisma client is available")
        return True
    except ImportError:
        logger.info("❌ Prisma client not available, setting up...")
        return setup_with_fallback()


def setup_with_fallback() -> bool:
    """
    Setup Prisma client with fallback options.
    
    Returns:
        True if setup successful, False otherwise
    """
    current_dir = Path(__file__).parent
    
    try:
        # Try prisma generate
        logger.info("🔄 Generating Prisma client...")
        run_command("prisma generate", cwd=current_dir)
        logger.info("✅ Prisma client generated successfully")
        
        # Verify the client works
        try:
            from prisma import Prisma
            logger.info("✅ Prisma client import successful")
            return True
        except ImportError as e:
            logger.error(f"❌ Prisma client import failed after generation: {e}")
            return False
            
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to generate Prisma client: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        
        # Try alternative setup approaches
        return try_alternative_setup(current_dir)
    except Exception as e:
        logger.error(f"❌ Unexpected error during setup: {e}")
        return False


def try_alternative_setup(current_dir: Path) -> bool:
    """
    Try alternative setup methods if standard setup fails.
    
    Args:
        current_dir: Current directory path
        
    Returns:
        True if any alternative worked, False otherwise
    """
    alternatives = [
        "python -m prisma generate",
        "python3 -m prisma generate", 
        f"cd {current_dir} && prisma generate",
    ]
    
    for cmd in alternatives:
        try:
            logger.info(f"🔄 Trying alternative: {cmd}")
            run_command(cmd, cwd=current_dir)
            
            # Test if it worked
            try:
                from prisma import Prisma
                logger.info("✅ Alternative setup successful")
                return True
            except ImportError:
                continue
                
        except subprocess.CalledProcessError as e:
            logger.debug(f"Alternative failed: {e}")
            continue
    
    logger.error("❌ All setup alternatives failed")
    return False


def setup_database() -> bool:
    """
    Setup the database schema.
    
    Returns:
        True if setup successful, False otherwise
    """
    current_dir = Path(__file__).parent
    
    try:
        logger.info("🔄 Setting up database schema...")
        run_command("prisma db push", cwd=current_dir)
        logger.info("✅ Database schema setup successful")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Database setup failed (this may be normal): {e}")
        # Database setup failure is not critical for client generation
        return True
    except Exception as e:
        logger.error(f"❌ Unexpected error during database setup: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up Coffee Club Event Indexer...")
    
    # Step 1: Generate Prisma client
    if not setup_with_fallback():
        print("❌ Failed to set up Prisma client")
        print("Please run 'prisma generate' manually in the coffee_club_indexer directory")
        sys.exit(1)
    
    # Step 2: Setup database (optional, may fail in some environments)
    setup_database()
    
    print("✅ Coffee Club Event Indexer setup complete!")
    print("You can now run 'python indexer.py' to start the indexer")


if __name__ == "__main__":
    main() 