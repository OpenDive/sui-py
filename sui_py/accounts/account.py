"""
Single key pair account implementation.
"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from .base import AbstractAccount
from ..exceptions import SuiValidationError

if TYPE_CHECKING:
    from ..crypto.base import AbstractPrivateKey, AbstractPublicKey
    from ..crypto.signature import Signature
    from ..crypto.schemes import SignatureScheme
    from ..types.base import SuiAddress


@dataclass(frozen=True)
class Account(AbstractAccount):
    """
    A Sui account representing a single key pair.
    
    This class supports all Sui signature schemes (Ed25519, Secp256k1, Secp256r1)
    and provides a unified interface for:
    - Address derivation
    - Message signing
    - Signature verification
    - Key management
    
    The account is immutable once created for security.
    
    Examples:
        # Generate new accounts
        ed25519_account = Account.generate(SignatureScheme.ED25519)
        secp256k1_account = Account.generate(SignatureScheme.SECP256K1)
        
        # Import from existing keys
        account = Account.from_hex("0x123...", SignatureScheme.ED25519)
        account = Account.from_private_key(existing_private_key)
        
        # Use the account
        address = account.address
        signature = account.sign(message_bytes)
    """
    _private_key: "AbstractPrivateKey"
    _address: Optional["SuiAddress"] = field(default=None, init=False)
    
    def __post_init__(self):
        """Validate the account on creation."""
        if self._private_key is None:
            raise SuiValidationError("Private key cannot be None")
    
    @classmethod
    def generate(cls, scheme: "SignatureScheme") -> "Account":
        """
        Generate a new account with a random private key.
        
        Args:
            scheme: The signature scheme to use (Ed25519, Secp256k1, or Secp256r1)
            
        Returns:
            A new account with a randomly generated key pair
            
        Raises:
            ValueError: If the signature scheme is not supported
            NotImplementedError: If the scheme is not yet implemented
            
        Examples:
            account = Account.generate(SignatureScheme.ED25519)
            secp_account = Account.generate(SignatureScheme.SECP256K1)
        """
        from ..crypto import create_private_key
        private_key = create_private_key(scheme)
        return cls(private_key)
    
    @classmethod
    def from_private_key(cls, private_key: "AbstractPrivateKey") -> "Account":
        """
        Create an account from an existing private key.
        
        Args:
            private_key: The private key to use for this account
            
        Returns:
            An account using the provided private key
            
        Raises:
            SuiValidationError: If the private key is invalid
            
        Examples:
            private_key = Ed25519PrivateKey.generate()
            account = Account.from_private_key(private_key)
        """
        if private_key is None:
            raise SuiValidationError("Private key cannot be None")
        return cls(private_key)
    
    @classmethod
    def from_hex(cls, hex_string: str, scheme: "SignatureScheme") -> "Account":
        """
        Create an account from a hex-encoded private key.
        
        Args:
            hex_string: The private key as hex (with or without 0x prefix)
            scheme: The signature scheme to use
            
        Returns:
            An account using the imported private key
            
        Raises:
            ValueError: If the hex string is invalid
            SuiValidationError: If the key is invalid for the scheme
            NotImplementedError: If the scheme is not yet implemented
            
        Examples:
            account = Account.from_hex("0x123...", SignatureScheme.ED25519)
        """
        from ..crypto import import_private_key
        
        if not isinstance(hex_string, str):
            raise SuiValidationError("Hex string must be a string")
        
        # Remove 0x prefix if present
        hex_clean = hex_string.lower()
        if hex_clean.startswith("0x"):
            hex_clean = hex_clean[2:]
        
        try:
            key_bytes = bytes.fromhex(hex_clean)
            private_key = import_private_key(key_bytes, scheme)
            return cls(private_key)
        except ValueError as e:
            raise SuiValidationError(f"Invalid hex string: {e}")
    
    @classmethod
    def from_bytes(cls, key_bytes: bytes, scheme: "SignatureScheme") -> "Account":
        """
        Create an account from private key bytes.
        
        Args:
            key_bytes: The private key as bytes
            scheme: The signature scheme to use
            
        Returns:
            An account using the imported private key
            
        Raises:
            SuiValidationError: If the key bytes are invalid
            NotImplementedError: If the scheme is not yet implemented
            
        Examples:
            key_bytes = b'\\x01\\x02...'  # 32 bytes for most schemes
            account = Account.from_bytes(key_bytes, SignatureScheme.ED25519)
        """
        from ..crypto import import_private_key
        
        if not isinstance(key_bytes, bytes):
            raise SuiValidationError("Key bytes must be bytes")
        
        private_key = import_private_key(key_bytes, scheme)
        return cls(private_key)
    
    @classmethod
    def from_base64(cls, base64_string: str, scheme: "SignatureScheme") -> "Account":
        """
        Create an account from a base64-encoded private key.
        
        Args:
            base64_string: The private key as base64
            scheme: The signature scheme to use
            
        Returns:
            An account using the imported private key
            
        Raises:
            SuiValidationError: If the base64 string is invalid
            NotImplementedError: If the scheme is not yet implemented
            
        Examples:
            account = Account.from_base64("SGVsbG8gV29ybGQ=", SignatureScheme.ED25519)
        """
        import base64
        
        if not isinstance(base64_string, str):
            raise SuiValidationError("Base64 string must be a string")
        
        try:
            key_bytes = base64.b64decode(base64_string)
            return cls.from_bytes(key_bytes, scheme)
        except Exception as e:
            raise SuiValidationError(f"Invalid base64 string: {e}")
    
    @property
    def address(self) -> "SuiAddress":
        """
        Get the Sui address for this account.
        
        The address is derived from the public key using BLAKE2b hashing
        and is cached for performance.
        
        Returns:
            The Sui address for this account
        """
        if self._address is None:
            # Use object.__setattr__ since the dataclass is frozen
            object.__setattr__(self, '_address', self._private_key.public_key().to_sui_address())
        return self._address
    
    @property
    def public_key(self) -> "AbstractPublicKey":
        """
        Get the public key for this account.
        
        Returns:
            The public key derived from the private key
        """
        return self._private_key.public_key()
    
    @property
    def scheme(self) -> "SignatureScheme":
        """
        Get the signature scheme used by this account.
        
        Returns:
            The signature scheme (Ed25519, Secp256k1, or Secp256r1)
        """
        return self._private_key.scheme
    
    @property
    def private_key(self) -> "AbstractPrivateKey":
        """
        Get the private key for this account.
        
        ⚠️  WARNING: Handle private keys with extreme care.
        Never log, print, or transmit private keys in plaintext.
        
        Returns:
            The private key instance
        """
        return self._private_key
    
    def sign(self, message: bytes) -> "Signature":
        """
        Sign a message with this account's private key.
        
        Args:
            message: The message bytes to sign
            
        Returns:
            The signature over the message
            
        Raises:
            SuiValidationError: If the message is invalid or signing fails
            
        Examples:
            message = b"Hello, Sui!"
            signature = account.sign(message)
        """
        if not isinstance(message, bytes):
            raise SuiValidationError("Message must be bytes")
        
        return self._private_key.sign(message)
    
    def verify(self, message: bytes, signature: "Signature") -> bool:
        """
        Verify a signature against a message using this account's public key.
        
        Args:
            message: The original message bytes
            signature: The signature to verify
            
        Returns:
            True if the signature is valid, False otherwise
            
        Examples:
            message = b"Hello, Sui!"
            signature = account.sign(message)
            is_valid = account.verify(message, signature)  # True
        """
        if not isinstance(message, bytes):
            raise SuiValidationError("Message must be bytes")
        
        return self.public_key.verify(message, signature)
    
    def to_dict(self) -> dict:
        """
        Export account information as a dictionary.
        
        ⚠️  WARNING: This includes the private key in hex format.
        Only use this for secure storage or serialization.
        
        Returns:
            Dictionary containing account information
            
        Examples:
            account_data = account.to_dict()
            # Save to secure storage...
        """
        return {
            "scheme": self.scheme.value,
            "private_key": self._private_key.to_hex(),
            "public_key": self.public_key.to_hex(),
            "address": str(self.address)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        """
        Create an account from a dictionary (e.g., loaded from storage).
        
        Args:
            data: Dictionary containing account information
            
        Returns:
            An account instance
            
        Raises:
            SuiValidationError: If the data is invalid
            KeyError: If required keys are missing
            
        Examples:
            data = {"scheme": "ED25519", "private_key": "0x123..."}
            account = Account.from_dict(data)
        """
        try:
            from ..crypto.schemes import SignatureScheme
            
            scheme_str = data["scheme"]
            private_key_hex = data["private_key"]
            
            # Convert scheme string to enum
            scheme = SignatureScheme(scheme_str)
            
            return cls.from_hex(private_key_hex, scheme)
        except KeyError as e:
            raise SuiValidationError(f"Missing required key in account data: {e}")
        except ValueError as e:
            raise SuiValidationError(f"Invalid account data: {e}")
    
    def export_private_key_hex(self) -> str:
        """
        Export the private key as a hex string.
        
        ⚠️  WARNING: Handle with extreme care.
        Never log, print, or transmit private keys in plaintext.
        
        Returns:
            The private key as hex string with 0x prefix
        """
        return self._private_key.to_hex()
    
    def export_private_key_base64(self) -> str:
        """
        Export the private key as a base64 string.
        
        ⚠️  WARNING: Handle with extreme care.
        Never log, print, or transmit private keys in plaintext.
        
        Returns:
            The private key as base64 string
        """
        return self._private_key.to_base64()
    
    def export_public_key_hex(self) -> str:
        """
        Export the public key as a hex string.
        
        Returns:
            The public key as hex string with 0x prefix
        """
        return self.public_key.to_hex()
    
    def export_public_key_base64(self) -> str:
        """
        Export the public key as a base64 string.
        
        Returns:
            The public key as base64 string
        """
        return self.public_key.to_base64() 