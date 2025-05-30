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
    Generate the Prisma client.
    
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
        
        print("📦 Generating Prisma client... (this may take a moment)")
        
        # Run prisma generate
        result = subprocess.run(
            ["prisma", "generate"],
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes timeout
        )
        
        if result.returncode == 0:
            # Create success marker
            SETUP_MARKER.touch()
            print("✅ Database client ready!")
            return True
        else:
            print("❌ Failed to generate Prisma client.")
            print(f"   Error: {result.stderr.strip()}")
            print()
            print("💡 Try running manually:")
            print(f"   cd {INDEXER_DIR}")
            print("   prisma generate")
            print()
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Prisma generation timed out.")
        print("   This might be due to network issues downloading the Prisma engine.")
        print()
        print("💡 Try running manually:")
        print(f"   cd {INDEXER_DIR}")
        print("   prisma generate")
        print()
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error during Prisma generation: {e}")
        print()
        print("💡 Try running manually:")
        print(f"   cd {INDEXER_DIR}")
        print("   prisma generate")
        print()
        return False
        
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def ensure_prisma_client() -> bool:
    """
    Ensure the Prisma client is available and up-to-date.
    
    This function:
    1. Checks if the client already exists
    2. Checks if the schema has changed
    3. Auto-generates the client if needed
    4. Provides helpful error messages if generation fails
    
    Returns:
        True if the client is ready, False if setup failed
    """
    # Skip if client exists and schema hasn't changed
    if prisma_client_exists() and not schema_changed():
        return True
    
    # Need to generate or regenerate
    if prisma_client_exists():
        print("🔄 Schema changed, updating database client...")
    
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
    print("3. (Optional) Set up the database:")
    print("   prisma db push")
    print()
    print("4. Run the indexer:")
    print("   python indexer.py")
    print()
    print("If you continue to have issues, please check:")
    print("- Prisma Client Python is properly installed")
    print("- You have internet access (Prisma downloads binaries)")
    print("- You have write permissions in the current directory")
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