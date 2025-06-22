"""
Coffee machine controller for the Coffee Club Event Indexer.

This module provides integration with physical coffee machines via async subprocess calls,
mirroring the TypeScript implementation's approach of calling external Python controllers.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CoffeeMachineController:
    """
    Controller for interfacing with coffee machines.
    
    This class provides async methods for triggering coffee making via external
    controller scripts, handling errors gracefully and providing detailed logging.
    """
    
    def __init__(self, mac_address: str, controller_path: str, enabled: bool = True):
        """
        Initialize the coffee machine controller.
        
        Args:
            mac_address: MAC address of the coffee machine
            controller_path: Path to the external controller script
            enabled: Whether coffee machine integration is enabled
        """
        self.mac_address = mac_address
        self.controller_path = controller_path
        self.enabled = enabled
        
        # Validate controller path on initialization
        if self.enabled:
            self._validate_controller()
    
    def _validate_controller(self) -> None:
        """Validate that the controller script exists and is accessible."""
        controller_file = Path(self.controller_path)
        
        if not controller_file.exists():
            logger.warning(
                f"Coffee machine controller not found at {self.controller_path}. "
                f"Coffee machine integration will be disabled."
            )
            self.enabled = False
            return
        
        if not controller_file.is_file():
            logger.warning(
                f"Controller path {self.controller_path} is not a file. "
                f"Coffee machine integration will be disabled."
            )
            self.enabled = False
            return
        
        logger.info(f"Coffee machine controller validated at {self.controller_path}")
    
    async def make_coffee(self, coffee_type: str, order_id: str) -> bool:
        """
        Trigger coffee making for a specific order.
        
        Args:
            coffee_type: Type of coffee to make (espresso, americano, etc.)
            order_id: ID of the order being processed
            
        Returns:
            True if coffee making was triggered successfully, False otherwise
        """
        if not self.enabled:
            logger.warning(f"Coffee machine disabled, skipping order {order_id}")
            return False
        
        if not self.mac_address or self.mac_address == "00:00:00:00:00:00":
            logger.error("Coffee machine MAC address not configured properly")
            return False
        
        logger.info(f"🚀 Triggering coffee machine for order {order_id}: {coffee_type}")
        
        try:
            # Construct the command to run the controller
            cmd = [
                "python3.13",  # Use specific Python version as in TypeScript
                self.controller_path,
                self.mac_address,
                coffee_type.lower()
            ]
            
            logger.debug(f"Executing command: {' '.join(cmd)}")
            
            # Run the controller asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=60.0  # 60 second timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"Coffee machine controller timed out for order {order_id}")
                process.kill()
                return False
            
            # Process the results
            if process.returncode == 0:
                output = stdout.decode().strip()
                logger.info(f"☕ Coffee machine output for {order_id}: {output}")
                return True
            else:
                error = stderr.decode().strip()
                logger.error(f"❌ Coffee machine error for {order_id}: {error}")
                return False
                
        except FileNotFoundError:
            logger.error(f"Python interpreter or controller not found: {self.controller_path}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to trigger coffee machine for {order_id}: {e}")
            return False
    
    def is_valid_coffee_type(self, coffee_type: str, valid_types: list) -> bool:
        """
        Validate that the coffee type is supported.
        
        Args:
            coffee_type: The coffee type to validate
            valid_types: List of valid coffee types
            
        Returns:
            True if the coffee type is valid, False otherwise
        """
        return coffee_type.lower() in [t.lower() for t in valid_types]
    
    def extract_coffee_type(self, order_object: dict, valid_types: list, default: str = "espresso") -> str:
        """
        Extract coffee type from order object with robust parsing.
        
        Args:
            order_object: The order object from the blockchain
            valid_types: List of valid coffee types
            default: Default coffee type if extraction fails
            
        Returns:
            The extracted coffee type or default if not found/invalid
        """
        try:
            # Navigate to the content fields
            content = order_object.get("data", {}).get("content", {})
            if not content or "fields" not in content:
                logger.warning("Order object missing content or fields")
                return default
            
            fields = content["fields"]
            
            # Try different possible formats for coffee_type field
            coffee_type_data = fields.get("coffee_type")
            if not coffee_type_data:
                logger.warning("Order object missing coffee_type field")
                return default
            
            coffee_type = None
            
            # Format 1: { variant: "Espresso" }
            if isinstance(coffee_type_data, dict) and "variant" in coffee_type_data:
                coffee_type = coffee_type_data["variant"]
            
            # Format 2: { fields: { name: "Espresso" } }
            elif (isinstance(coffee_type_data, dict) and 
                  "fields" in coffee_type_data and 
                  isinstance(coffee_type_data["fields"], dict) and
                  "name" in coffee_type_data["fields"]):
                coffee_type = coffee_type_data["fields"]["name"]
            
            # Format 3: "Espresso" (string directly)
            elif isinstance(coffee_type_data, str):
                coffee_type = coffee_type_data
            
            if coffee_type:
                coffee_type = coffee_type.lower()
                if self.is_valid_coffee_type(coffee_type, valid_types):
                    return coffee_type
                else:
                    logger.warning(f"Invalid coffee type '{coffee_type}', using default '{default}'")
            
        except Exception as e:
            logger.error(f"Error extracting coffee type: {e}")
        
        return default 