from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .AbstractSignature import AbstractSignature
    from ..schemes import SignatureScheme
    from ..intent import IntentScope
    from ...types.base import SuiAddress
    
class AbstractPublicKey(ABC):
    """
    Abstract base class for public keys across all signature schemes.
    """
    
    @classmethod
    @abstractmethod
    def from_bytes(cls, key_bytes: bytes) -> "AbstractPublicKey":
        """
        Create a public key from raw bytes.
        
        Args:
            key_bytes: The public key bytes
            
        Returns:
            A public key instance
            
        Raises:
            ValueError: If the key bytes are invalid
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_hex(cls, hex_string: str) -> "AbstractPublicKey":
        """
        Create a public key from a hex string.
        
        Args:
            hex_string: The public key as hex (with or without 0x prefix)
            
        Returns:
            A public key instance
            
        Raises:
            ValueError: If the hex string is invalid
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_base64(cls, base64_string: str) -> "AbstractPublicKey":
        """
        Create a public key from a base64 string.
        
        Args:
            base64_string: The public key as base64
            
        Returns:
            A public key instance
            
        Raises:
            ValueError: If the base64 string is invalid
        """
        pass
    
    @abstractmethod
    def verify(self, message: bytes, signature: "AbstractSignature") -> bool:
        """
        Verify a signature against a message.
        
        Args:
            message: The original message bytes
            signature: The signature to verify
            
        Returns:
            True if the signature is valid, False otherwise
        """
        pass
    
    def verify_with_intent(
        self, 
        message: bytes, 
        signature: "AbstractSignature",
        intent_scope: "IntentScope"
    ) -> bool:
        """
        Verify a signature against a message with intent wrapping.
        
        This method handles the intent-based signature verification used by Sui:
        1. Wraps the message with the specified intent scope
        2. Hashes the intent message with BLAKE2b-256
        3. Verifies the signature against the hash
        
        Args:
            message: The original message bytes (pre-serialized for the intent)
            signature: The signature to verify
            intent_scope: The intent scope (TransactionData, PersonalMessage, etc.)
            
        Returns:
            True if the signature is valid, False otherwise
            
        Raises:
            SuiValidationError: If parameters are invalid
            
        Examples:
            # Verify a personal message signature
            public_key.verify_with_intent(
                message_bytes,
                signature, 
                IntentScope.PersonalMessage
            )
        """
        from ..intent import message_with_intent, hash_intent_message
        
        # Wrap message with intent and hash
        intent_message = message_with_intent(intent_scope, message)
        digest = hash_intent_message(intent_message)
        
        # Verify signature against the digest
        return self.verify(digest, signature)
    
    def verify_personal_message(
        self,
        message: bytes,
        signature: "AbstractSignature"
    ) -> bool:
        """
        Verify a signature for a personal message.
        
        This is a convenience method that handles the complete personal message
        verification process:
        1. Serializes the message as BCS vector<u8>
        2. Wraps with PersonalMessage intent
        3. Hashes with BLAKE2b-256
        4. Verifies the signature
        
        This matches the TypeScript SDK's verifyPersonalMessage() method.
        
        Args:
            message: The raw message bytes to verify
            signature: The signature to verify
            
        Returns:
            True if the signature is valid, False otherwise
            
        Raises:
            SuiValidationError: If parameters are invalid
            
        Examples:
            message = b"Hello, Sui blockchain!"
            if public_key.verify_personal_message(message, signature):
                print("Valid signature!")
        """
        from ..intent import message_with_intent_for_personal_message, hash_intent_message
        
        # Wrap personal message with intent (includes vector<u8> serialization)
        intent_message = message_with_intent_for_personal_message(message)
        digest = hash_intent_message(intent_message)
        
        # Verify signature against the digest
        return self.verify(digest, signature)
    
    def verify_transaction(
        self,
        transaction: bytes,
        signature: "AbstractSignature"
    ) -> bool:
        """
        Verify a signature for a transaction.
        
        This is a convenience method for transaction verification:
        1. Wraps transaction bytes with TransactionData intent
        2. Hashes with BLAKE2b-256
        3. Verifies the signature
        
        Args:
            transaction: The BCS-serialized transaction bytes
            signature: The signature to verify
            
        Returns:
            True if the signature is valid, False otherwise
            
        Raises:
            SuiValidationError: If parameters are invalid
            
        Examples:
            tx_bytes = transaction.to_bytes()
            if public_key.verify_transaction(tx_bytes, signature):
                print("Valid transaction signature!")
        """
        from ..intent import IntentScope, message_with_intent, hash_intent_message
        
        # Wrap transaction with intent
        intent_message = message_with_intent(IntentScope.TransactionData, transaction)
        digest = hash_intent_message(intent_message)
        
        # Verify signature against the digest
        return self.verify(digest, signature)
    
    @abstractmethod
    def to_sui_address(self) -> "SuiAddress":
        """
        Derive the Sui address from this public key.
        
        Returns:
            The Sui address
        """
        pass
    
    @abstractmethod
    def to_bytes(self) -> bytes:
        """
        Export the public key as bytes.
        
        Returns:
            The public key bytes
        """
        pass
    
    @abstractmethod
    def to_hex(self) -> str:
        """
        Export the public key as a hex string.
        
        Returns:
            The public key as hex string with 0x prefix
        """
        pass
    
    @abstractmethod
    def to_base64(self) -> str:
        """
        Export the public key as a base64 string.
        
        Returns:
            The public key as base64 string
        """
        pass
    
    @property
    @abstractmethod
    def scheme(self) -> "SignatureScheme":
        """
        Get the signature scheme for this key.
        
        Returns:
            The signature scheme
        """
        pass

