"""
Hierarchical Deterministic (HD) Wallet implementation.

Provides BIP32/BIP39 compatible HD wallet functionality for Sui blockchain,
supporting multiple signature schemes and account management.
"""

import hashlib
import hmac
from typing import Dict, List, Optional, Union, TYPE_CHECKING
from dataclasses import dataclass, field

from mnemonic import Mnemonic

from ..accounts import Account
from ..crypto import SignatureScheme, import_private_key
from .derivation import DerivationPath, SuiDerivationPath
from .exceptions import InvalidMnemonicError, DerivationError, WalletError

if TYPE_CHECKING:
    from ..client import SuiClient


@dataclass
class HDWallet:
    """
    Hierarchical Deterministic Wallet for Sui blockchain.
    
    Manages multiple accounts derived from a single mnemonic seed phrase.
    Each account is a complete Account instance supporting all Sui operations.
    Follows BIP32/BIP39 standards with Sui-specific derivation paths.
    
    Examples:
        # Generate new wallet
        wallet = HDWallet.generate()
        account = wallet.derive_account(0, SignatureScheme.ED25519)
        
        # Restore from mnemonic
        wallet = HDWallet.from_mnemonic("word1 word2 ...")
        accounts = wallet.list_accounts()
        
        # Multi-scheme support
        ed25519_account = wallet.derive_account(0, SignatureScheme.ED25519)
        secp256k1_account = wallet.derive_account(0, SignatureScheme.SECP256K1)
    """
    _mnemonic: str
    _seed: bytes = field(init=False)
    _accounts: Dict[str, Account] = field(default_factory=dict, init=False)
    _language: str = field(default="english", init=False)
    
    def __post_init__(self):
        """Initialize the wallet and validate the mnemonic."""
        # Validate mnemonic
        if not self.validate_mnemonic(self._mnemonic):
            raise InvalidMnemonicError(f"Invalid mnemonic phrase")
        
        # Generate seed from mnemonic
        object.__setattr__(self, '_seed', self._mnemonic_to_seed(self._mnemonic))
    
    @classmethod
    def generate(cls, word_count: int = 12, language: str = "english") -> "HDWallet":
        """
        Generate a new HD wallet with a random mnemonic.
        
        Args:
            word_count: Number of words in mnemonic (12, 15, 18, 21, or 24)
            language: Language for mnemonic words (default: english)
            
        Returns:
            A new HDWallet instance
            
        Raises:
            WalletError: If word count is invalid
            
        Examples:
            wallet = HDWallet.generate()  # 12 words
            wallet = HDWallet.generate(24)  # 24 words
        """
        if word_count not in [12, 15, 18, 21, 24]:
            raise WalletError(f"Invalid word count: {word_count}. Must be 12, 15, 18, 21, or 24")
        
        # Calculate entropy bits based on word count
        entropy_bits = (word_count * 11) - (word_count // 3)
        
        mnemo = Mnemonic(language)
        mnemonic_phrase = mnemo.generate(entropy_bits)
        
        wallet = cls(mnemonic_phrase)
        object.__setattr__(wallet, '_language', language)
        return wallet
    
    @classmethod
    def from_mnemonic(cls, mnemonic: str, language: str = "english") -> "HDWallet":
        """
        Create an HD wallet from an existing mnemonic phrase.
        
        Args:
            mnemonic: The mnemonic phrase (12-24 words)
            language: Language of the mnemonic words
            
        Returns:
            HDWallet instance
            
        Raises:
            InvalidMnemonicError: If the mnemonic is invalid
            
        Examples:
            wallet = HDWallet.from_mnemonic("abandon abandon abandon...")
        """
        wallet = cls(mnemonic.strip())
        object.__setattr__(wallet, '_language', language)
        return wallet
    
    @staticmethod
    def validate_mnemonic(mnemonic: str, language: str = "english") -> bool:
        """
        Validate a mnemonic phrase.
        
        Args:
            mnemonic: The mnemonic phrase to validate
            language: Language of the mnemonic words
            
        Returns:
            True if the mnemonic is valid, False otherwise
        """
        try:
            mnemo = Mnemonic(language)
            return mnemo.check(mnemonic.strip())
        except Exception:
            return False
    
    def _mnemonic_to_seed(self, mnemonic: str, passphrase: str = "") -> bytes:
        """
        Convert mnemonic to seed using PBKDF2.
        
        Args:
            mnemonic: The mnemonic phrase
            passphrase: Optional passphrase for additional security
            
        Returns:
            64-byte seed
        """
        mnemo = Mnemonic(self._language)
        return mnemo.to_seed(mnemonic, passphrase)
    
    def _derive_key_at_path(self, path: DerivationPath, scheme: SignatureScheme) -> bytes:
        """
        Derive a private key at the specified derivation path.
        
        Args:
            path: BIP32 derivation path
            scheme: Signature scheme for the derived key
            
        Returns:
            Private key bytes
            
        Raises:
            DerivationError: If derivation fails
        """
        try:
            # Start with master key from seed
            master_key = self._derive_master_key()
            
            # Derive at each component of the path
            current_key = master_key
            for component in path.components:
                current_key = self._derive_child_key(current_key, component)
            
            # Extract the private key portion (first 32 bytes)
            private_key_bytes = current_key[:32]
            
            # Validate key length for the scheme
            expected_lengths = {
                SignatureScheme.ED25519: 32,
                SignatureScheme.SECP256K1: 32,
                SignatureScheme.SECP256R1: 32,
            }
            
            expected_length = expected_lengths.get(scheme, 32)
            if len(private_key_bytes) != expected_length:
                raise DerivationError(f"Invalid key length for {scheme}: {len(private_key_bytes)}")
            
            return private_key_bytes
            
        except Exception as e:
            raise DerivationError(f"Failed to derive key at path {path}: {e}")
    
    def _derive_master_key(self) -> bytes:
        """
        Derive the master private key from the seed.
        
        Returns:
            64-byte master key (32 bytes key + 32 bytes chain code)
        """
        # BIP32 master key derivation
        hmac_sha512 = hmac.new(b"ed25519 seed", self._seed, hashlib.sha512)
        return hmac_sha512.digest()
    
    def _derive_child_key(self, parent_key: bytes, index: int) -> bytes:
        """
        Derive a child key from parent key using BIP32.
        
        Args:
            parent_key: 64-byte parent key (32 bytes key + 32 bytes chain code)
            index: Child index (>= 2^31 for hardened)
            
        Returns:
            64-byte child key
        """
        # Split parent key into key and chain code
        parent_private_key = parent_key[:32]
        parent_chain_code = parent_key[32:]
        
        # Prepare data for HMAC
        if index >= 0x80000000:  # Hardened derivation
            data = b'\x00' + parent_private_key + index.to_bytes(4, 'big')
        else:  # Non-hardened derivation (not recommended for private keys)
            # For non-hardened, we would need the public key, but for security
            # we'll treat all derivations as hardened for private keys
            data = b'\x00' + parent_private_key + index.to_bytes(4, 'big')
        
        # Derive child key and chain code
        hmac_sha512 = hmac.new(parent_chain_code, data, hashlib.sha512)
        child_key_data = hmac_sha512.digest()
        
        return child_key_data
    
    def _account_cache_key(self, path: DerivationPath, scheme: SignatureScheme) -> str:
        """Generate cache key for an account."""
        return f"{path.path}#{scheme.value}"
    
    @property
    def mnemonic(self) -> str:
        """
        Get the mnemonic phrase.
        
        ⚠️  WARNING: Handle mnemonic with extreme care.
        Never log, print, or transmit mnemonic in plaintext.
        Store securely and consider encryption.
        
        Returns:
            The mnemonic phrase
        """
        return self._mnemonic
    
    @property
    def accounts(self) -> Dict[str, Account]:
        """
        Get all cached accounts.
        
        Returns:
            Dictionary mapping cache keys to Account instances
        """
        return self._accounts.copy()
    
    def derive_account(self, account_index: int, scheme: SignatureScheme) -> Account:
        """
        Derive an account at the standard Sui derivation path.
        
        Uses the path: m/44'/784'/0'/0'/account_index'
        
        Args:
            account_index: Account index (0, 1, 2, ...)
            scheme: Signature scheme for the account
            
        Returns:
            Account instance
            
        Examples:
            account = wallet.derive_account(0, SignatureScheme.ED25519)
            secp_account = wallet.derive_account(1, SignatureScheme.SECP256K1)
        """
        path = SuiDerivationPath.standard_account(account_index)
        return self.derive_account_at_path(path, scheme)
    
    def derive_account_at_path(self, path: DerivationPath, scheme: SignatureScheme) -> Account:
        """
        Derive an account at a custom derivation path.
        
        Args:
            path: Custom derivation path
            scheme: Signature scheme for the account
            
        Returns:
            Account instance
            
        Raises:
            DerivationError: If derivation fails
            
        Examples:
            path = DerivationPath("m/44'/784'/0'/0'/5'")
            account = wallet.derive_account_at_path(path, SignatureScheme.ED25519)
        """
        cache_key = self._account_cache_key(path, scheme)
        
        # Return cached account if available
        if cache_key in self._accounts:
            return self._accounts[cache_key]
        
        # Derive new account
        try:
            private_key_bytes = self._derive_key_at_path(path, scheme)
            private_key = import_private_key(private_key_bytes, scheme)
            account = Account.from_private_key(private_key)
            
            # Cache the account
            self._accounts[cache_key] = account
            
            return account
            
        except Exception as e:
            raise DerivationError(f"Failed to derive account at {path} with {scheme}: {e}")
    
    def get_account(self, account_index: int, scheme: SignatureScheme) -> Account:
        """
        Get an account (derive if not cached).
        
        This is an alias for derive_account() for convenience.
        
        Args:
            account_index: Account index
            scheme: Signature scheme
            
        Returns:
            Account instance
        """
        return self.derive_account(account_index, scheme)
    
    def list_accounts(self) -> List[Account]:
        """
        List all cached accounts.
        
        Returns:
            List of Account instances
        """
        return list(self._accounts.values())
    
    def add_account(self, scheme: SignatureScheme) -> Account:
        """
        Add a new account with the next available index.
        
        Args:
            scheme: Signature scheme for the new account
            
        Returns:
            Newly created Account instance
        """
        # Find the next available index for this scheme
        existing_indices = set()
        for cache_key in self._accounts.keys():
            if cache_key.endswith(f"#{scheme.value}"):
                # Extract account index from standard path
                path_part = cache_key.split('#')[0]
                if "44'/784'/0'/0'/" in path_part:
                    try:
                        index_part = path_part.split("44'/784'/0'/0'/")[1].rstrip("'")
                        existing_indices.add(int(index_part))
                    except (IndexError, ValueError):
                        continue
        
        # Find next available index
        next_index = 0
        while next_index in existing_indices:
            next_index += 1
        
        return self.derive_account(next_index, scheme)
    
    async def discover_accounts(
        self, 
        client: "SuiClient", 
        schemes: Optional[List[SignatureScheme]] = None,
        max_empty_accounts: int = 10
    ) -> List[Account]:
        """
        Discover accounts with on-chain activity.
        
        Sequentially derives accounts and checks for blockchain activity.
        Stops after finding max_empty_accounts consecutive empty accounts.
        
        Args:
            client: SuiClient for checking account activity
            schemes: List of signature schemes to check (defaults to all supported)
            max_empty_accounts: Number of consecutive empty accounts before stopping
            
        Returns:
            List of accounts with discovered activity
            
        Examples:
            client = SuiClient("https://fullnode.mainnet.sui.io:443")
            active_accounts = await wallet.discover_accounts(client)
        """
        if schemes is None:
            schemes = [SignatureScheme.ED25519, SignatureScheme.SECP256K1]
        
        discovered_accounts = []
        
        for scheme in schemes:
            empty_count = 0
            account_index = 0
            
            while empty_count < max_empty_accounts:
                try:
                    # Derive account
                    account = self.derive_account(account_index, scheme)
                    
                    # Check for activity (simplified - could be enhanced)
                    try:
                        # Check if account has any objects
                        objects = await client.get_owned_objects(account.address)
                        has_activity = len(objects.data) > 0
                        
                        if has_activity:
                            discovered_accounts.append(account)
                            empty_count = 0  # Reset counter
                        else:
                            empty_count += 1
                            
                    except Exception:
                        # If we can't check activity, assume empty
                        empty_count += 1
                    
                    account_index += 1
                    
                except Exception:
                    # If derivation fails, stop
                    break
        
        return discovered_accounts
    
    def export_mnemonic(self) -> str:
        """
        Export the mnemonic phrase.
        
        ⚠️  WARNING: Handle with extreme care.
        Never log, print, or transmit mnemonic in plaintext.
        
        Returns:
            The mnemonic phrase
        """
        return self._mnemonic
    
    def export_wallet_data(self, include_mnemonic: bool = True) -> dict:
        """
        Export wallet data for storage.
        
        ⚠️  WARNING: The exported data contains sensitive information.
        Encrypt before storing and handle with extreme care.
        
        Args:
            include_mnemonic: Whether to include mnemonic in export
            
        Returns:
            Dictionary containing wallet data
        """
        data = {
            "version": "1.0",
            "language": self._language,
            "accounts": {}
        }
        
        if include_mnemonic:
            data["mnemonic"] = self._mnemonic
        
        # Export account information (without private keys for security)
        for cache_key, account in self._accounts.items():
            path_str, scheme_str = cache_key.split('#')
            data["accounts"][cache_key] = {
                "path": path_str,
                "scheme": scheme_str,
                "address": str(account.address),
                "public_key": account.export_public_key_hex()
            }
        
        return data
    
    @classmethod
    def from_wallet_data(cls, data: dict) -> "HDWallet":
        """
        Create wallet from exported data.
        
        Args:
            data: Dictionary containing wallet data
            
        Returns:
            HDWallet instance
            
        Raises:
            WalletError: If data is invalid or incomplete
        """
        try:
            mnemonic = data["mnemonic"]
            language = data.get("language", "english")
            
            wallet = cls.from_mnemonic(mnemonic, language)
            
            # Re-derive accounts mentioned in the data
            accounts_data = data.get("accounts", {})
            for cache_key, account_info in accounts_data.items():
                path_str = account_info["path"]
                scheme_str = account_info["scheme"]
                
                path = DerivationPath(path_str)
                scheme = SignatureScheme(scheme_str)
                
                # Derive the account (this will cache it)
                wallet.derive_account_at_path(path, scheme)
            
            return wallet
            
        except KeyError as e:
            raise WalletError(f"Missing required field in wallet data: {e}")
        except Exception as e:
            raise WalletError(f"Failed to restore wallet from data: {e}")
    
    def __str__(self) -> str:
        """String representation."""
        account_count = len(self._accounts)
        return f"HDWallet(accounts={account_count})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"HDWallet("
            f"accounts={len(self._accounts)}, "
            f"language='{self._language}'"
            f")"
        ) 