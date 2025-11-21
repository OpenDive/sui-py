"""
Intent-based message signing for Sui blockchain.

This module provides the intent system used by Sui to ensure that signed messages
are tied to specific purposes and domains. Intents prevent signature reuse across
different contexts (e.g., a transaction signature can't be used as a personal message).

The intent system wraps messages with metadata (scope, version, app ID) before signing,
creating a domain separator that binds the signature to its intended use.
"""

import hashlib
from enum import IntEnum
from dataclasses import dataclass
from typing import Generic, TypeVar, TYPE_CHECKING

from ..bcs import BcsSerializable, Serializer, Deserializer, BcsVector, U8, bcs_vector
from ..exceptions import SuiValidationError

if TYPE_CHECKING:
    pass


class IntentScope(IntEnum):
    """
    Scope of an intent, defining the purpose of the signed message.
    
    This enum matches the Sui blockchain's intent scope system:
    - TransactionData: For signing transaction blocks
    - TransactionEffects: For signing transaction effects (typically validators)
    - CheckpointSummary: For signing checkpoint summaries (validators)
    - PersonalMessage: For signing arbitrary personal messages
    """
    TransactionData = 0
    TransactionEffects = 1
    CheckpointSummary = 2
    PersonalMessage = 3


class IntentVersion(IntEnum):
    """
    Version of the intent structure.
    
    Currently only V0 is defined in the Sui protocol.
    """
    V0 = 0


class AppId(IntEnum):
    """
    Application ID for the intent.
    
    Currently only Sui is defined in the protocol.
    """
    Sui = 0


@dataclass(frozen=True)
class Intent(BcsSerializable):
    """
    Intent structure that provides domain separation for signatures.
    
    An intent consists of:
    - scope: What the message is for (transaction, personal message, etc.)
    - version: Protocol version (currently always V0)
    - app_id: Application identifier (currently always Sui)
    
    The intent is prepended to messages before hashing and signing, ensuring
    that signatures are bound to their specific purpose.
    """
    scope: IntentScope
    version: IntentVersion
    app_id: AppId
    
    def __post_init__(self):
        """Validate intent fields."""
        if not isinstance(self.scope, IntentScope):
            raise SuiValidationError(f"Invalid intent scope: {self.scope}")
        if not isinstance(self.version, IntentVersion):
            raise SuiValidationError(f"Invalid intent version: {self.version}")
        if not isinstance(self.app_id, AppId):
            raise SuiValidationError(f"Invalid app ID: {self.app_id}")
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the intent to BCS format.
        
        Format:
        - scope: u8 (enum variant)
        - version: u8 (enum variant)
        - app_id: u8 (enum variant)
        """
        serializer.write_u8(self.scope.value)
        serializer.write_u8(self.version.value)
        serializer.write_u8(self.app_id.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> "Intent":
        """Deserialize an intent from BCS format."""
        scope = IntentScope(deserializer.read_u8())
        version = IntentVersion(deserializer.read_u8())
        app_id = AppId(deserializer.read_u8())
        return cls(scope=scope, version=version, app_id=app_id)
    
    @classmethod
    def transaction_data(cls) -> "Intent":
        """Create an intent for transaction data."""
        return cls(
            scope=IntentScope.TransactionData,
            version=IntentVersion.V0,
            app_id=AppId.Sui
        )
    
    @classmethod
    def personal_message(cls) -> "Intent":
        """Create an intent for personal messages."""
        return cls(
            scope=IntentScope.PersonalMessage,
            version=IntentVersion.V0,
            app_id=AppId.Sui
        )
    
    @classmethod
    def transaction_effects(cls) -> "Intent":
        """Create an intent for transaction effects."""
        return cls(
            scope=IntentScope.TransactionEffects,
            version=IntentVersion.V0,
            app_id=AppId.Sui
        )
    
    @classmethod
    def checkpoint_summary(cls) -> "Intent":
        """Create an intent for checkpoint summaries."""
        return cls(
            scope=IntentScope.CheckpointSummary,
            version=IntentVersion.V0,
            app_id=AppId.Sui
        )


# Type variable for intent message values
T = TypeVar('T')


@dataclass(frozen=True)
class IntentMessage(BcsSerializable, Generic[T]):
    """
    Generic intent message wrapper.
    
    An IntentMessage wraps a value with an intent, creating a complete
    message structure that can be hashed and signed.
    
    The BCS serialization format is:
    - intent: Intent (3 bytes: scope, version, app_id)
    - value: T (serialized according to type T)
    
    Type parameter:
        T: The type of value being wrapped (must be BCS-serializable)
    """
    intent: Intent
    value: bytes  # Pre-serialized value bytes
    
    def __post_init__(self):
        """Validate intent message fields."""
        if not isinstance(self.intent, Intent):
            raise SuiValidationError("intent must be an Intent instance")
        if not isinstance(self.value, bytes):
            raise SuiValidationError("value must be bytes")
    
    def serialize(self, serializer: Serializer) -> None:
        """
        Serialize the intent message to BCS format.
        
        Format:
        - intent: Intent (3 bytes)
        - value: bytes (raw, already serialized)
        """
        self.intent.serialize(serializer)
        serializer.write_bytes(self.value)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> "IntentMessage":
        """Deserialize an intent message from BCS format."""
        intent = Intent.deserialize(deserializer)
        # Read remaining bytes as value
        remaining = deserializer.remaining_bytes()
        value = deserializer.read_bytes(remaining)
        return cls(intent=intent, value=value)
    
    def to_bytes(self) -> bytes:
        """Get the complete serialized intent message."""
        serializer = Serializer()
        self.serialize(serializer)
        return serializer.to_bytes()


def message_with_intent(scope: IntentScope, message: bytes) -> bytes:
    """
    Wrap a message with an intent and serialize it.
    
    This is the core function for creating intent messages. It:
    1. Creates an Intent with the specified scope
    2. Wraps the message bytes in an IntentMessage
    3. Serializes the complete structure to BCS bytes
    
    These bytes are then hashed (BLAKE2b-256) and signed.
    
    Args:
        scope: The intent scope (TransactionData, PersonalMessage, etc.)
        message: The message bytes to wrap
        
    Returns:
        The complete BCS-serialized intent message
        
    Raises:
        SuiValidationError: If parameters are invalid
        
    Examples:
        # For personal messages
        intent_msg = message_with_intent(IntentScope.PersonalMessage, b"Hello, Sui!")
        
        # For transactions
        intent_msg = message_with_intent(IntentScope.TransactionData, tx_bytes)
    """
    if not isinstance(scope, IntentScope):
        raise SuiValidationError(f"scope must be an IntentScope, got {type(scope)}")
    if not isinstance(message, bytes):
        raise SuiValidationError(f"message must be bytes, got {type(message)}")
    
    # Create intent with the specified scope
    intent = Intent(
        scope=scope,
        version=IntentVersion.V0,
        app_id=AppId.Sui
    )
    
    # Wrap message in intent message structure
    intent_message = IntentMessage(intent=intent, value=message)
    
    # Serialize and return
    return intent_message.to_bytes()


def message_with_intent_for_personal_message(message: bytes) -> bytes:
    """
    Wrap a personal message with intent and serialize it.
    
    Personal messages must be wrapped as vector<u8> before adding intent.
    This function handles both steps:
    1. Serialize message as BCS vector<u8> (length prefix + bytes)
    2. Wrap with PersonalMessage intent
    
    Args:
        message: The raw message bytes
        
    Returns:
        The complete BCS-serialized intent message ready for hashing
        
    Examples:
        msg = b"Hello, Sui blockchain!"
        intent_msg = message_with_intent_for_personal_message(msg)
        # Now hash with BLAKE2b and sign
    """
    if not isinstance(message, bytes):
        raise SuiValidationError(f"message must be bytes, got {type(message)}")
    
    # Serialize message as vector<u8> (BCS format: length prefix + bytes)
    message_vector = bcs_vector([U8(b) for b in message])
    serializer = Serializer()
    message_vector.serialize(serializer)
    message_bytes = serializer.to_bytes()
    
    # Wrap with PersonalMessage intent
    return message_with_intent(IntentScope.PersonalMessage, message_bytes)


def hash_intent_message(intent_message_bytes: bytes) -> bytes:
    """
    Hash an intent message using BLAKE2b-256.
    
    This is the standard hash function used by Sui for all signatures.
    The intent message bytes are hashed to produce a 32-byte digest,
    which is then signed.
    
    Args:
        intent_message_bytes: The serialized intent message
        
    Returns:
        32-byte BLAKE2b hash digest
        
    Examples:
        intent_msg = message_with_intent_for_personal_message(b"Hello!")
        digest = hash_intent_message(intent_msg)
        signature = private_key.sign(digest)
    """
    if not isinstance(intent_message_bytes, bytes):
        raise SuiValidationError(f"intent_message_bytes must be bytes")
    
    return hashlib.blake2b(intent_message_bytes, digest_size=32).digest()

