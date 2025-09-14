"""
Move Utils API client for Sui blockchain.

Provides methods for introspecting Move packages, modules, functions, and structs.
"""

from typing import Any, Dict, List, Union

from .rest_client import RestClient
from ..exceptions import SuiValidationError
from ..types.move_utils import (
    SuiMoveFunctionArgType,
    SuiMoveNormalizedFunction,
    SuiMoveNormalizedModule,
    SuiMoveNormalizedStruct
)


class MoveUtilsAPIClient:
    """
    Client for Sui Move Utils API operations.
    
    Provides methods for introspecting Move packages, modules, functions, and structs.
    All methods return typed objects corresponding to the Sui JSON-RPC API schemas.
    
    Implements the five core Move Utils API RPC methods:
    - sui_getMoveFunctionArgTypes
    - sui_getNormalizedMoveFunction
    - sui_getNormalizedMoveModule
    - sui_getNormalizedMoveModulesByPackage
    - sui_getNormalizedMoveStruct
    """
    
    def __init__(self, rest_client: RestClient):
        """
        Initialize the Move Utils API client.
        
        Args:
            rest_client: The underlying REST client for making RPC calls
        """
        self.rest_client = rest_client
    
    async def get_move_function_arg_types(
        self,
        package: str,
        module: str,
        function: str
    ) -> List[SuiMoveFunctionArgType]:
        """
        Get Move function argument types like read, write and full access.
        
        Args:
            package: The package address (e.g., "0x2")
            module: The module name (e.g., "coin")
            function: The function name (e.g., "transfer")
            
        Returns:
            List of Move function argument types
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If parameters are invalid
        """
        if not package:
            raise SuiValidationError("Package address is required")
        if not module:
            raise SuiValidationError("Module name is required")
        if not function:
            raise SuiValidationError("Function name is required")
        
        params = [package, module, function]
        result = await self.rest_client.call("sui_getMoveFunctionArgTypes", params)
        return [SuiMoveFunctionArgType.from_dict(arg_type) for arg_type in result]
    
    async def get_normalized_move_function(
        self,
        package: str,
        module: str,
        function: str
    ) -> SuiMoveNormalizedFunction:
        """
        Get a structured representation of Move function.
        
        Args:
            package: The package address (e.g., "0x2")
            module: The module name (e.g., "coin")
            function: The function name (e.g., "transfer")
            
        Returns:
            Normalized Move function representation
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If parameters are invalid
        """
        if not package:
            raise SuiValidationError("Package address is required")
        if not module:
            raise SuiValidationError("Module name is required")
        if not function:
            raise SuiValidationError("Function name is required")
        
        params = [package, module, function]
        result = await self.rest_client.call("sui_getNormalizedMoveFunction", params)
        return SuiMoveNormalizedFunction.from_dict(result)
    
    async def get_normalized_move_module(
        self,
        package: str,
        module: str
    ) -> SuiMoveNormalizedModule:
        """
        Get a structured representation of Move module.
        
        Args:
            package: The package address (e.g., "0x2")
            module: The module name (e.g., "coin")
            
        Returns:
            Normalized Move module representation
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If parameters are invalid
        """
        if not package:
            raise SuiValidationError("Package address is required")
        if not module:
            raise SuiValidationError("Module name is required")
        
        params = [package, module]
        result = await self.rest_client.call("sui_getNormalizedMoveModule", params)
        return SuiMoveNormalizedModule.from_dict(result)
    
    async def get_normalized_move_modules_by_package(
        self,
        package: str
    ) -> Dict[str, SuiMoveNormalizedModule]:
        """
        Get a map from module name to structured representations of Move modules.
        
        Args:
            package: The package address (e.g., "0x2")
            
        Returns:
            Dictionary mapping module names to normalized Move modules
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If parameters are invalid
        """
        if not package:
            raise SuiValidationError("Package address is required")
        
        params = [package]
        result = await self.rest_client.call("sui_getNormalizedMoveModulesByPackage", params)
        
        modules = {}
        for module_name, module_data in result.items():
            modules[module_name] = SuiMoveNormalizedModule.from_dict(module_data)
        
        return modules
    
    async def get_normalized_move_struct(
        self,
        package: str,
        module: str,
        struct: str
    ) -> SuiMoveNormalizedStruct:
        """
        Get a structured representation of Move struct.
        
        Args:
            package: The package address (e.g., "0x2")
            module: The module name (e.g., "coin")
            struct: The struct name (e.g., "Coin")
            
        Returns:
            Normalized Move struct representation
            
        Raises:
            SuiRPCError: If the RPC call fails
            SuiValidationError: If parameters are invalid
        """
        if not package:
            raise SuiValidationError("Package address is required")
        if not module:
            raise SuiValidationError("Module name is required")
        if not struct:
            raise SuiValidationError("Struct name is required")
        
        params = [package, module, struct]
        result = await self.rest_client.call("sui_getNormalizedMoveStruct", params)
        return SuiMoveNormalizedStruct.from_dict(result)
