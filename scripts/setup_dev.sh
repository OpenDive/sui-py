#!/bin/bash
# Development environment setup script for SuiPy (Bash version)

set -e  # Exit on any error

echo "🚀 Setting up SuiPy development environment"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/venv"

echo "Project root: $PROJECT_ROOT"

# Check if virtual environment exists
if [ -d "$VENV_PATH" ]; then
    read -p "Virtual environment already exists at $VENV_PATH. Recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf "$VENV_PATH"
    else
        echo "Using existing virtual environment."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install production dependencies
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "Installing production dependencies..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
fi

# Install development dependencies
if [ -f "$PROJECT_ROOT/requirements-dev.txt" ]; then
    echo "Installing development dependencies..."
    pip install -r "$PROJECT_ROOT/requirements-dev.txt"
fi

# Install package in development mode
echo "Installing SuiPy in development mode..."
cd "$PROJECT_ROOT"
pip install -e .

echo
echo "✅ Development environment setup complete!"
echo
echo "To activate the virtual environment:"
echo "  source $VENV_PATH/bin/activate"
echo
echo "To run the example:"
echo "  python examples/coin_query_example.py"
echo
echo "To run tests (when available):"
echo "  pytest" 