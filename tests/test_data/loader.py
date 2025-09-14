"""
Utility functions for loading test data JSON files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List


def load_json(filename: str) -> Dict[str, Any]:
    """
    Load JSON test data file.
    
    Args:
        filename: Relative path to JSON file (e.g., "write_api/execute_transaction_block_success.json")
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        json.JSONDecodeError: If the JSON is malformed
    """
    base_path = Path(__file__).parent
    file_path = base_path / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Test data file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_all_samples(api_type: str) -> Dict[str, Dict[str, Any]]:
    """
    Load all JSON samples for a specific API type.
    
    Args:
        api_type: API type directory name ("write_api", "read_api", "move_utils")
        
    Returns:
        Dictionary mapping filename to JSON data
    """
    base_path = Path(__file__).parent
    api_path = base_path / api_type
    
    if not api_path.exists():
        raise FileNotFoundError(f"API type directory not found: {api_path}")
    
    samples = {}
    for json_file in api_path.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            samples[json_file.stem] = json.load(f)
    
    return samples


def get_sample_names(api_type: str) -> List[str]:
    """
    Get list of available sample file names for an API type.
    
    Args:
        api_type: API type directory name
        
    Returns:
        List of sample file names (without .json extension)
    """
    base_path = Path(__file__).parent
    api_path = base_path / api_type
    
    if not api_path.exists():
        return []
    
    return [f.stem for f in api_path.glob("*.json")]
