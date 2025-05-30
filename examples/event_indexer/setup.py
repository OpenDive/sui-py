"""
Auto-setup module for the SuiPy Event Indexer.

This module automatically handles Prisma client generation to provide
a seamless developer experience. Users can run the example without
needing to manually run external commands.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Get the directory containing this file
INDEXER_DIR = Path(__file__).parent
PRISMA_DIR = INDEXER_DIR / "prisma"
SCHEMA_FILE = INDEXER_DIR / "schema.prisma"
SETUP_MARKER = INDEXER_DIR / ".prisma_ready"


def prisma_client_exists() -> bool:
    """Check if the Prisma client has been generated."""
    # Check for the generated client directory and key files
    client_file = PRISMA_DIR / "client.py"
    models_file = PRISMA_DIR / "models.py"
    
    return (
        PRISMA_DIR.exists() and 
        client_file.exists() and 
        models_file.exists() and
        SETUP_MARKER.exists()
    )


def prisma_cli_available() -> bool:
    """Check if the Prisma CLI is available."""
    try:
        result = subprocess.run(
            ["prisma", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def database_tables_exist() -> bool:
    """Check if the database tables have been created."""
    try:
        # Try to connect to the database and check for tables
        # We'll use a simple approach - check if the database file exists for SQLite
        from .config import CONFIG
        
        if CONFIG.database_url.startswith("file:"):
            # SQLite database
            db_path = CONFIG.database_url.replace("file:", "")
            db_file = INDEXER_DIR / db_path.lstrip("./")
            return db_file.exists()
        else:
            # For other databases, assume tables exist if client is generated
            # This is a simplification - in production you'd want to check the actual tables
            return prisma_client_exists()
    except Exception:
        return False


def schema_changed() -> bool:
    """Check if the schema has changed since last generation."""
    if not SETUP_MARKER.exists():
        return True
    
    if not SCHEMA_FILE.exists():
        return False
    
    try:
        schema_mtime = SCHEMA_FILE.stat().st_mtime
        marker_mtime = SETUP_MARKER.stat().st_mtime
        return schema_mtime > marker_mtime
    except OSError:
        return True


def generate_prisma_client() -> bool:
    """
    Generate the Prisma client and create database tables.
    
    Returns:
        True if generation was successful, False otherwise
    """
    print("🔧 Setting up database client...")
    
    # Check if Prisma CLI is available
    if not prisma_cli_available():
        print("❌ Prisma CLI not found.")
        print("   The 'prisma' command is not available in your PATH.")
        print("   This usually means Prisma Client Python installation is incomplete.")
        print()
        print("💡 To fix this, try:")
        print("   pip install --force-reinstall prisma")
        print("   prisma generate")
        print()
        return False
    
    # Ensure we're in the correct directory
    original_cwd = os.getcwd()
    
    try:
        # Change to the indexer directory where schema.prisma is located
        os.chdir(INDEXER_DIR)
        
        # Ensure DATABASE_URL is set in environment
        env = os.environ.copy()
        try:
            from .config import CONFIG
            env["DATABASE_URL"] = CONFIG.database_url
        except ImportError:
            # Fallback to default if config import fails
            env["DATABASE_URL"] = "file:./indexer.db"
        
        print("📦 Generating Prisma client... (this may take a moment)")
        
        # Run prisma generate
        result = subprocess.run(
            ["prisma", "generate"],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutes timeout
            env=env
        )
        
        if result.returncode != 0:
            print("❌ Failed to generate Prisma client.")
            print(f"   Error: {result.stderr.strip()}")
            print()
            print("💡 Try running manually:")
            print(f"   cd {INDEXER_DIR}")
            print("   prisma generate")
            print()
            return False
        
        print("✅ Prisma client generated!")
        
        # Now create the database tables
        print("🗄️  Creating database tables...")
        
        db_result = subprocess.run(
            ["prisma", "db", "push"],
            capture_output=True,
            text=True,
            timeout=60,  # 1 minute timeout
            env=env
        )
        
        if db_result.returncode == 0:
            # Create success marker
            SETUP_MARKER.touch()
            print("✅ Database ready!")
            return True
        else:
            print("❌ Failed to create database tables.")
            print(f"   Error: {db_result.stderr.strip()}")
            print()
            print("💡 Try running manually:")
            print(f"   cd {INDEXER_DIR}")
            print("   prisma db push")
            print()
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Database setup timed out.")
        print("   This might be due to network issues downloading the Prisma engine.")
        print()
        print("💡 Try running manually:")
        print(f"   cd {INDEXER_DIR}")
        print("   prisma generate")
        print("   prisma db push")
        print()
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error during database setup: {e}")
        print()
        print("💡 Try running manually:")
        print(f"   cd {INDEXER_DIR}")
        print("   prisma generate")
        print("   prisma db push")
        print()
        return False
        
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def ensure_prisma_client() -> bool:
    """
    Ensure the Prisma client is available and database is set up.
    
    This function:
    1. Checks if the client already exists
    2. Checks if the database tables exist
    3. Checks if the schema has changed
    4. Auto-generates the client and creates tables if needed
    5. Provides helpful error messages if setup fails
    
    Returns:
        True if the client and database are ready, False if setup failed
    """
    # Skip if client exists, database exists, and schema hasn't changed
    if (prisma_client_exists() and 
        database_tables_exist() and 
        not schema_changed()):
        return True
    
    # Need to generate or regenerate
    if prisma_client_exists() and database_tables_exist():
        print("🔄 Schema changed, updating database...")
    elif prisma_client_exists():
        print("🔄 Database tables missing, creating...")
    
    return generate_prisma_client()


def show_manual_setup_instructions():
    """Show manual setup instructions if auto-setup fails."""
    print()
    print("📋 Manual Setup Instructions:")
    print("=" * 50)
    print("1. Navigate to the event indexer directory:")
    print(f"   cd {INDEXER_DIR}")
    print()
    print("2. Generate the Prisma client:")
    print("   prisma generate")
    print()
    print("3. Create the database tables:")
    print("   prisma db push")
    print()
    print("4. Run the indexer:")
    print("   python indexer.py")
    print()
    print("If you continue to have issues, please check:")
    print("- Prisma Client Python is properly installed")
    print("- You have internet access (Prisma downloads binaries)")
    print("- You have write permissions in the current directory")
    print("- The schema.prisma file exists and is valid")
    print()


def setup_with_fallback() -> bool:
    """
    Attempt auto-setup with graceful fallback to manual instructions.
    
    Returns:
        True if setup succeeded, False if manual intervention needed
    """
    try:
        return ensure_prisma_client()
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        show_manual_setup_instructions()
        return False


if __name__ == "__main__":
    """Allow running setup directly: python setup.py"""
    print("SuiPy Event Indexer - Database Setup")
    print("=" * 40)
    
    if setup_with_fallback():
        print("\n🎉 Setup complete! You can now run the indexer.")
    else:
        print("\n⚠️  Setup incomplete. Please follow the manual instructions above.")
        sys.exit(1) 