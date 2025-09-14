#!/usr/bin/env python3
"""
Move Utils API Example for SuiPy SDK

This example demonstrates how to use the Move Utils API to introspect Move packages,
modules, functions, and structs on the Sui blockchain.

Usage:
    python3 examples/move_utils_example.py [network] [package] [module] [function]

Examples:
    python3 examples/move_utils_example.py testnet
    python3 examples/move_utils_example.py testnet 0x2
    python3 examples/move_utils_example.py testnet 0x2 coin
    python3 examples/move_utils_example.py testnet 0x2 coin transfer

Parameters:
    network: Network to connect to (mainnet, testnet, devnet, localnet)
             Defaults to 'testnet'
    package: Package address to analyze (e.g., '0x2')
    module:  Module name to analyze (e.g., 'coin')
    function: Function name to analyze (e.g., 'transfer')

The example will demonstrate:
- Function argument type analysis
- Module structure exploration
- Package discovery and analysis
- Struct field introspection
- Real-world Move introspection patterns
"""

import asyncio
import sys
from typing import Optional

from sui_py import SuiClient


async def demonstrate_function_analysis(client: SuiClient):
    """Demonstrate Move function argument type analysis."""
    print("=== Function Analysis ===")
    
    # Analyze common Sui functions
    functions_to_analyze = [
        ("0x2", "coin", "balance"),
        ("0x2", "transfer", "public_transfer"),
        ("0x2", "object", "delete"),
        ("0x1", "option", "some"),
    ]
    
    for package, module, function in functions_to_analyze:
        print(f"\n🔍 Analyzing {package}::{module}::{function}")
        
        try:
            # Get function argument types
            arg_types = await client.move_utils.get_move_function_arg_types(
                package=package,
                module=module,
                function=function
            )
            
            print(f"   ✅ Function found with {len(arg_types)} argument types")
            
            # Get detailed function information
            func_details = await client.move_utils.get_normalized_move_function(
                package=package,
                module=module,
                function=function
            )
            
            print(f"   📋 Visibility: {func_details.visibility}")
            print(f"   🚪 Entry function: {func_details.is_entry}")
            print(f"   📝 Parameters: {len(func_details.parameters)}")
            print(f"   🔄 Return types: {len(func_details.return_)}")
            
            if func_details.parameters:
                print(f"   📥 Parameter types:")
                for i, param in enumerate(func_details.parameters):
                    print(f"      {i}: {param}")
            
            if func_details.return_:
                print(f"   📤 Return types:")
                for i, ret_type in enumerate(func_details.return_):
                    print(f"      {i}: {ret_type}")
                    
        except Exception as e:
            print(f"   ❌ Error analyzing function: {e}")
    
    print()


async def demonstrate_module_exploration(client: SuiClient):
    """Demonstrate Move module structure exploration."""
    print("=== Module Exploration ===")
    
    # Analyze core Sui modules
    modules_to_explore = [
        ("0x2", "coin"),
        ("0x2", "object"),
        ("0x2", "transfer"),
        ("0x1", "option"),
    ]
    
    for package, module in modules_to_explore:
        print(f"\n🏗️  Exploring {package}::{module}")
        
        try:
            module_info = await client.move_utils.get_normalized_move_module(
                package=package,
                module=module
            )
            
            print(f"   ✅ Module found")
            print(f"   📍 Address: {module_info.address}")
            print(f"   📛 Name: {module_info.name}")
            print(f"   📄 File format version: {module_info.file_format_version}")
            print(f"   👥 Friends: {len(module_info.friends)}")
            print(f"   🏗️  Structs: {len(module_info.structs)}")
            print(f"   🔧 Functions: {len(module_info.exposed_functions)}")
            
            # Show available structs
            if module_info.structs:
                print(f"   📦 Available structs:")
                for struct_name in list(module_info.structs.keys())[:5]:  # Show first 5
                    print(f"      • {struct_name}")
                if len(module_info.structs) > 5:
                    print(f"      ... and {len(module_info.structs) - 5} more")
            
            # Show available functions
            if module_info.exposed_functions:
                print(f"   🔧 Available functions:")
                for func_name in list(module_info.exposed_functions.keys())[:5]:  # Show first 5
                    func = module_info.exposed_functions[func_name]
                    entry_marker = " (entry)" if func.is_entry else ""
                    print(f"      • {func_name}{entry_marker}")
                if len(module_info.exposed_functions) > 5:
                    print(f"      ... and {len(module_info.exposed_functions) - 5} more")
                    
        except Exception as e:
            print(f"   ❌ Error exploring module: {e}")
    
    print()


async def demonstrate_package_analysis(client: SuiClient):
    """Demonstrate complete package analysis."""
    print("=== Package Analysis ===")
    
    # Analyze core Sui packages
    packages_to_analyze = ["0x1", "0x2"]
    
    for package in packages_to_analyze:
        print(f"\n📦 Analyzing package {package}")
        
        try:
            all_modules = await client.move_utils.get_normalized_move_modules_by_package(
                package=package
            )
            
            print(f"   ✅ Package found with {len(all_modules)} modules")
            
            # Show module summary
            print(f"   📋 Available modules:")
            for module_name in list(all_modules.keys())[:10]:  # Show first 10
                module = all_modules[module_name]
                print(f"      • {module_name} ({len(module.exposed_functions)} functions, {len(module.structs)} structs)")
            
            if len(all_modules) > 10:
                print(f"      ... and {len(all_modules) - 10} more modules")
            
            # Calculate package statistics
            total_functions = sum(len(module.exposed_functions) for module in all_modules.values())
            total_structs = sum(len(module.structs) for module in all_modules.values())
            
            print(f"   📊 Package statistics:")
            print(f"      Total modules: {len(all_modules)}")
            print(f"      Total functions: {total_functions}")
            print(f"      Total structs: {total_structs}")
                    
        except Exception as e:
            print(f"   ❌ Error analyzing package: {e}")
    
    print()


async def demonstrate_struct_analysis(client: SuiClient):
    """Demonstrate Move struct field analysis."""
    print("=== Struct Analysis ===")
    
    # Analyze common Sui structs
    structs_to_analyze = [
        ("0x2", "coin", "Coin"),
        ("0x2", "object", "UID"),
        ("0x1", "option", "Option"),
    ]
    
    for package, module, struct in structs_to_analyze:
        print(f"\n🏗️  Analyzing {package}::{module}::{struct}")
        
        try:
            struct_info = await client.move_utils.get_normalized_move_struct(
                package=package,
                module=module,
                struct=struct
            )
            
            print(f"   ✅ Struct found")
            print(f"   🔧 Abilities: {struct_info.abilities}")
            print(f"   📝 Type parameters: {len(struct_info.type_parameters)}")
            print(f"   📋 Fields: {len(struct_info.fields)}")
            
            # Show struct fields
            if struct_info.fields:
                print(f"   📦 Field details:")
                for field in struct_info.fields:
                    field_name = field.get("name", "unknown")
                    field_type = field.get("type", "unknown")
                    print(f"      • {field_name}: {field_type}")
            
            # Show type parameters
            if struct_info.type_parameters:
                print(f"   🔤 Type parameters:")
                for i, type_param in enumerate(struct_info.type_parameters):
                    print(f"      {i}: {type_param}")
                    
        except Exception as e:
            print(f"   ❌ Error analyzing struct: {e}")
    
    print()


async def demonstrate_custom_analysis(client: SuiClient, package: str, module: Optional[str] = None, function: Optional[str] = None):
    """Demonstrate analysis of user-specified package/module/function."""
    print("=== Custom Analysis ===")
    
    if function and module:
        # Analyze specific function
        print(f"🎯 Analyzing specific function: {package}::{module}::{function}")
        
        try:
            # Get function argument types
            arg_types = await client.move_utils.get_move_function_arg_types(
                package=package,
                module=module,
                function=function
            )
            
            # Get function details
            func_details = await client.move_utils.get_normalized_move_function(
                package=package,
                module=module,
                function=function
            )
            
            print(f"   ✅ Function analysis complete")
            print(f"   📋 Visibility: {func_details.visibility}")
            print(f"   🚪 Entry function: {func_details.is_entry}")
            print(f"   📥 Parameters ({len(func_details.parameters)}):")
            for i, param in enumerate(func_details.parameters):
                print(f"      {i}: {param}")
            print(f"   📤 Returns ({len(func_details.return_)}):")
            for i, ret_type in enumerate(func_details.return_):
                print(f"      {i}: {ret_type}")
                
        except Exception as e:
            print(f"   ❌ Error analyzing function: {e}")
            
    elif module:
        # Analyze specific module
        print(f"🎯 Analyzing specific module: {package}::{module}")
        
        try:
            module_info = await client.move_utils.get_normalized_move_module(
                package=package,
                module=module
            )
            
            print(f"   ✅ Module analysis complete")
            print(f"   📍 Address: {module_info.address}")
            print(f"   📛 Name: {module_info.name}")
            print(f"   🏗️  Structs ({len(module_info.structs)}):")
            for struct_name in module_info.structs.keys():
                print(f"      • {struct_name}")
            print(f"   🔧 Functions ({len(module_info.exposed_functions)}):")
            for func_name, func in module_info.exposed_functions.items():
                entry_marker = " (entry)" if func.is_entry else ""
                print(f"      • {func_name}{entry_marker}")
                
        except Exception as e:
            print(f"   ❌ Error analyzing module: {e}")
            
    else:
        # Analyze specific package
        print(f"🎯 Analyzing specific package: {package}")
        
        try:
            all_modules = await client.move_utils.get_normalized_move_modules_by_package(
                package=package
            )
            
            print(f"   ✅ Package analysis complete")
            print(f"   📦 Modules ({len(all_modules)}):")
            for module_name, module in all_modules.items():
                print(f"      • {module_name} ({len(module.exposed_functions)} functions, {len(module.structs)} structs)")
                
        except Exception as e:
            print(f"   ❌ Error analyzing package: {e}")
    
    print()


async def demonstrate_real_world_patterns(client: SuiClient):
    """Demonstrate real-world Move Utils usage patterns."""
    print("=== Real-World Usage Patterns ===")
    
    print("\n💡 Pattern 1: Smart Contract Interface Discovery")
    try:
        # Discover all entry functions in a package
        modules = await client.move_utils.get_normalized_move_modules_by_package("0x2")
        
        entry_functions = []
        for module_name, module in modules.items():
            for func_name, func in module.exposed_functions.items():
                if func.is_entry:
                    entry_functions.append(f"{module_name}::{func_name}")
        
        print(f"   📋 Found {len(entry_functions)} entry functions in package 0x2")
        for func in entry_functions[:5]:  # Show first 5
            print(f"      • {func}")
        if len(entry_functions) > 5:
            print(f"      ... and {len(entry_functions) - 5} more")
            
    except Exception as e:
        print(f"   ❌ Error in pattern 1: {e}")
    
    print("\n💡 Pattern 2: Function Signature Validation")
    try:
        # Validate a function signature before calling
        func_details = await client.move_utils.get_normalized_move_function("0x2", "transfer", "public_transfer")
        
        print(f"   🔍 Validating 0x2::transfer::public_transfer signature:")
        print(f"      Entry function: {func_details.is_entry}")
        print(f"      Expected parameters: {len(func_details.parameters)}")
        for i, param in enumerate(func_details.parameters):
            print(f"         {i}: {param}")
            
    except Exception as e:
        print(f"   ❌ Error in pattern 2: {e}")
    
    print("\n💡 Pattern 3: Type System Exploration")
    try:
        # Explore generic types and their constraints
        coin_struct = await client.move_utils.get_normalized_move_struct("0x2", "coin", "Coin")
        
        print(f"   🏗️  Exploring Coin<T> generic structure:")
        print(f"      Type parameters: {len(coin_struct.type_parameters)}")
        print(f"      Abilities: {coin_struct.abilities}")
        print(f"      Fields: {len(coin_struct.fields)}")
        
    except Exception as e:
        print(f"   ❌ Error in pattern 3: {e}")
    
    print()


async def main():
    """Main example function."""
    # Parse command line arguments
    network = sys.argv[1] if len(sys.argv) > 1 else "testnet"
    custom_package = sys.argv[2] if len(sys.argv) > 2 else None
    custom_module = sys.argv[3] if len(sys.argv) > 3 else None
    custom_function = sys.argv[4] if len(sys.argv) > 4 else None
    
    print(f"Move Utils API Example - Connecting to {network}")
    print("=" * 60)
    print("This example demonstrates Move package, module, function, and struct introspection.")
    print()
    
    try:
        async with SuiClient(network) as client:
            print(f"Connected to: {client.endpoint}")
            print()
            
            # Run demonstrations
            await demonstrate_function_analysis(client)
            await demonstrate_module_exploration(client)
            await demonstrate_package_analysis(client)
            await demonstrate_struct_analysis(client)
            
            # Custom analysis if parameters provided
            if custom_package:
                await demonstrate_custom_analysis(client, custom_package, custom_module, custom_function)
            
            await demonstrate_real_world_patterns(client)
            
            print("=== Example Complete ===")
            print("\nKey Takeaways:")
            print("- Move Utils API provides comprehensive introspection capabilities")
            print("- Function analysis helps understand call signatures and requirements")
            print("- Module exploration reveals available functionality")
            print("- Package analysis gives overview of entire smart contract systems")
            print("- Struct analysis helps understand data layouts and type constraints")
            print("- Real-world patterns enable dynamic contract interaction")
            
            print("\nCommon Use Cases:")
            print("- Smart contract development and testing")
            print("- dApp interface generation")
            print("- Documentation generation")
            print("- Type validation for Move calls")
            print("- Developer tooling and IDE support")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
