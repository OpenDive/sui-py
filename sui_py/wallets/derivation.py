"""
Derivation path utilities for HD wallets.

Provides utilities for working with BIP32 derivation paths and Sui-specific
derivation standards.
"""

import re
from typing import List, Optional
from dataclasses import dataclass

from .exceptions import DerivationError


@dataclass(frozen=True)
class DerivationPath:
    """
    Represents a BIP32 derivation path.
    
    Handles parsing, validation, and manipulation of hierarchical deterministic
    derivation paths in the format: m/purpose'/coin_type'/account'/change/address_index
    
    Examples:
        DerivationPath("m/44'/784'/0'/0'/0'")
        DerivationPath.from_components([44, 784, 0, 0, 0], hardened=[True, True, True, True, True])
    """
    path: str
    
    def __post_init__(self):
        """Validate the derivation path format."""
        if not self.is_valid():
            raise DerivationError(f"Invalid derivation path format: {self.path}")
    
    def is_valid(self) -> bool:
        """
        Validate the derivation path format.
        
        Returns:
            True if the path is a valid BIP32 derivation path
        """
        # Must start with 'm' or 'M'
        if not self.path.lower().startswith('m'):
            return False
        
        # Check the overall format: m/number'/number'/...
        pattern = r"^[mM](/\d+'?)*$"
        return bool(re.match(pattern, self.path))
    
    @property
    def components(self) -> List[int]:
        """
        Get the numeric components of the path.
        
        Returns:
            List of integers representing each level in the path
        """
        if self.path.lower() == 'm':
            return []
        
        parts = self.path.split('/')[1:]  # Skip 'm'
        components = []
        
        for part in parts:
            if part.endswith("'"):
                # Hardened derivation (add 2^31)
                components.append(int(part[:-1]) + 0x80000000)
            else:
                # Non-hardened derivation
                components.append(int(part))
        
        return components
    
    @property
    def hardened_components(self) -> List[bool]:
        """
        Get which components are hardened.
        
        Returns:
            List of booleans indicating hardened derivation for each component
        """
        if self.path.lower() == 'm':
            return []
        
        parts = self.path.split('/')[1:]  # Skip 'm'
        return [part.endswith("'") for part in parts]
    
    @classmethod
    def from_components(cls, components: List[int], hardened: Optional[List[bool]] = None) -> "DerivationPath":
        """
        Create a derivation path from numeric components.
        
        Args:
            components: List of integers for each derivation level
            hardened: List of booleans indicating hardened derivation (all hardened if None)
            
        Returns:
            A DerivationPath instance
            
        Examples:
            DerivationPath.from_components([44, 784, 0, 0, 0])
            DerivationPath.from_components([44, 784, 0], [True, True, False])
        """
        if hardened is None:
            # Default to all hardened
            hardened = [True] * len(components)
        
        if len(components) != len(hardened):
            raise DerivationError("Components and hardened lists must have the same length")
        
        path_parts = ["m"]
        for comp, is_hardened in zip(components, hardened):
            if is_hardened:
                path_parts.append(f"{comp}'")
            else:
                path_parts.append(str(comp))
        
        return cls("/".join(path_parts))
    
    def append(self, component: int, hardened: bool = False) -> "DerivationPath":
        """
        Append a component to the derivation path.
        
        Args:
            component: The numeric component to append
            hardened: Whether this component should be hardened
            
        Returns:
            A new DerivationPath with the component appended
        """
        suffix = f"{component}'" if hardened else str(component)
        new_path = f"{self.path}/{suffix}"
        return DerivationPath(new_path)
    
    def __str__(self) -> str:
        return self.path
    
    def __repr__(self) -> str:
        return f"DerivationPath('{self.path}')"


class SuiDerivationPath:
    """
    Sui-specific derivation path utilities.
    
    Provides standard derivation paths for Sui blockchain accounts
    following established conventions.
    """
    
    # Sui coin type (registered with SLIP-0044)
    SUI_COIN_TYPE = 784
    
    @staticmethod
    def standard_account(account_index: int) -> DerivationPath:
        """
        Generate standard Sui account derivation path.
        
        Uses the path: m/44'/784'/0'/0'/account_index'
        
        Args:
            account_index: The account index (0, 1, 2, ...)
            
        Returns:
            DerivationPath for the specified account
            
        Examples:
            SuiDerivationPath.standard_account(0)  # m/44'/784'/0'/0'/0'
            SuiDerivationPath.standard_account(1)  # m/44'/784'/0'/0'/1'
        """
        return DerivationPath.from_components(
            [44, SuiDerivationPath.SUI_COIN_TYPE, 0, 0, account_index],
            [True, True, True, True, True]  # All hardened
        )
    
    @staticmethod
    def custom_account(purpose: int, account: int, change: int, address_index: int) -> DerivationPath:
        """
        Generate custom Sui derivation path.
        
        Uses the path: m/purpose'/784'/account'/change'/address_index'
        
        Args:
            purpose: BIP43 purpose (typically 44 for BIP44)
            account: Account index
            change: Change index (typically 0 for external, 1 for internal)
            address_index: Address index within the account
            
        Returns:
            DerivationPath for the specified parameters
        """
        return DerivationPath.from_components(
            [purpose, SuiDerivationPath.SUI_COIN_TYPE, account, change, address_index],
            [True, True, True, True, True]  # All hardened for security
        )
    
    @staticmethod
    def legacy_account(account_index: int) -> DerivationPath:
        """
        Generate legacy-style derivation path for compatibility.
        
        Uses the path: m/44'/784'/account'/0/0
        
        Args:
            account_index: The account index
            
        Returns:
            DerivationPath for legacy compatibility
        """
        return DerivationPath.from_components(
            [44, SuiDerivationPath.SUI_COIN_TYPE, account_index, 0, 0],
            [True, True, True, False, False]  # Account level hardened
        )
    
    @staticmethod
    def validate_sui_path(path: DerivationPath) -> bool:
        """
        Validate that a derivation path is suitable for Sui.
        
        Args:
            path: The derivation path to validate
            
        Returns:
            True if the path is valid for Sui usage
        """
        try:
            components = path.components
            
            # Must have at least 3 components (purpose, coin_type, account)
            if len(components) < 3:
                return False
            
            # Check if coin type matches Sui (accounting for hardened bit)
            coin_type = components[1]
            sui_coin_type_hardened = SuiDerivationPath.SUI_COIN_TYPE + 0x80000000
            
            return coin_type == sui_coin_type_hardened
            
        except Exception:
            return False 