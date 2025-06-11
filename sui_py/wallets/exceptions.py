"""
Wallet-specific exceptions.
"""

from ..exceptions import SuiError


class WalletError(SuiError):
    """Base exception for wallet-related errors."""
    pass


class InvalidMnemonicError(WalletError):
    """Raised when a mnemonic phrase is invalid."""
    pass


class DerivationError(WalletError):
    """Raised when key derivation fails."""
    pass


class AccountDiscoveryError(WalletError):
    """Raised when account discovery encounters an error."""
    pass 