#!/usr/bin/env python3
"""
Ed25519 cryptographic functionality test suite.

This module tests the Ed25519 private key, public key, signing, verification,
serialization, and address derivation functionality to ensure compatibility
with Sui blockchain requirements.
"""

import pytest
import sys
import os
import base64
import secrets

# Add the parent directory to the path to import sui_py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sui_py import (
    SignatureScheme, 
    create_private_key,
    import_private_key,
    Ed25519PrivateKey, 
    Ed25519PublicKey,
    Signature,
    SuiValidationError
)
from sui_py.types.base import SuiAddress


# Test vectors from official Sui CLI (cross-platform compatibility)
# Generated using: cargo build --bin sui && sui client new-address ed25519
SUI_CLI_TEST_VECTORS = [
    {
        "raw_public_key": "UdGRWooy48vGTs0HBokIis5NK+DUjiWc9ENUlcfCCBE=",
        "sui_public_key": "AFHRkVqKMuPLxk7NBwaJCIrOTSvg1I4lnPRDVJXHwggR",
        "sui_address": "0xd77a6cd55073e98d4029b1b0b8bd8d88f45f343dad2732fc9a7965094e635c55",
    },
    {
        "raw_public_key": "0PTAfQmNiabgbak9U/stWZzKc5nsRqokda2qnV2DTfg=",
        "sui_public_key": "AND0wH0JjYmm4G2pPVP7LVmcynOZ7EaqJHWtqp1dg034",
        "sui_address": "0x7e8fd489c3d3cd9cc7cbcc577dc5d6de831e654edd9997d95c412d013e6eea23",
    },
    {
        "raw_public_key": "6L/l0uhGt//9cf6nLQ0+24Uv2qanX/R6tn7lWUJX1Xk=",
        "sui_public_key": "AOi/5dLoRrf//XH+py0NPtuFL9qmp1/0erZ+5VlCV9V5",
        "sui_address": "0x3a1b4410ebe9c3386a429c349ba7929aafab739c277f97f32622b971972a14a2",
    },
]


class TestEd25519PrivateKey:
    """Test cases for Ed25519 private key functionality."""
    
    def test_generate_private_key(self):
        """Test Ed25519 private key generation."""
        # Generate multiple keys to ensure randomness
        key1 = Ed25519PrivateKey.generate()
        key2 = Ed25519PrivateKey.generate()
        
        # Ensure they are different
        assert key1.to_bytes() != key2.to_bytes()
        
        # Ensure correct scheme
        assert key1.scheme == SignatureScheme.ED25519
        assert key2.scheme == SignatureScheme.ED25519
        
        # Ensure correct key length
        assert len(key1.to_bytes()) == 32
        assert len(key2.to_bytes()) == 32
    
    def test_factory_generate_private_key(self):
        """Test Ed25519 private key generation via factory function."""
        key = create_private_key(SignatureScheme.ED25519)
        
        assert isinstance(key, Ed25519PrivateKey)
        assert key.scheme == SignatureScheme.ED25519
        assert len(key.to_bytes()) == 32
    
    def test_from_bytes_valid(self):
        """Test creating Ed25519 private key from valid bytes."""
        # Generate valid 32-byte key
        key_bytes = secrets.token_bytes(32)
        key = Ed25519PrivateKey.from_bytes(key_bytes)
        
        assert key.scheme == SignatureScheme.ED25519
        assert key.to_bytes() == key_bytes
    
    def test_from_bytes_invalid_length(self):
        """Test creating Ed25519 private key from invalid length bytes."""
        # Test various invalid lengths
        invalid_lengths = [0, 1, 16, 31, 33, 64]
        
        for length in invalid_lengths:
            key_bytes = secrets.token_bytes(length)
            with pytest.raises(SuiValidationError, match="must be 32 bytes"):
                Ed25519PrivateKey.from_bytes(key_bytes)
    
    def test_from_bytes_invalid_type(self):
        """Test creating Ed25519 private key from non-bytes."""
        with pytest.raises(SuiValidationError, match="must be bytes"):
            Ed25519PrivateKey.from_bytes("not bytes")
    
    def test_from_hex_valid(self):
        """Test creating Ed25519 private key from valid hex string."""
        # Generate valid key and convert to hex
        original_key = Ed25519PrivateKey.generate()
        hex_string = original_key.to_hex()
        
        # Test with 0x prefix
        reconstructed_key = Ed25519PrivateKey.from_hex(hex_string)
        assert reconstructed_key.to_bytes() == original_key.to_bytes()
        
        # Test without 0x prefix
        hex_no_prefix = hex_string[2:]  # Remove 0x
        reconstructed_key_no_prefix = Ed25519PrivateKey.from_hex(hex_no_prefix)
        assert reconstructed_key_no_prefix.to_bytes() == original_key.to_bytes()
    
    def test_from_hex_invalid_length(self):
        """Test creating Ed25519 private key from invalid hex length."""
        # Test various invalid lengths
        invalid_hex_strings = [
            "0x",  # Empty
            "0x123",  # Too short
            "0x" + "a" * 63,  # 31.5 bytes
            "0x" + "a" * 65,  # 32.5 bytes
            "0x" + "a" * 128,  # 64 bytes
        ]
        
        for hex_string in invalid_hex_strings:
            with pytest.raises(SuiValidationError, match="must be 64 characters"):
                Ed25519PrivateKey.from_hex(hex_string)
    
    def test_from_hex_invalid_format(self):
        """Test creating Ed25519 private key from invalid hex format."""
        with pytest.raises(SuiValidationError, match="Invalid hex string"):
            Ed25519PrivateKey.from_hex("0x" + "g" * 64)  # Invalid hex char
        
        with pytest.raises(SuiValidationError, match="Hex string must be a string"):
            Ed25519PrivateKey.from_hex(123)  # Not a string
    
    def test_from_base64_valid(self):
        """Test creating Ed25519 private key from valid base64 string."""
        # Generate valid key and convert to base64
        original_key = Ed25519PrivateKey.generate()
        base64_string = original_key.to_base64()
        
        # Reconstruct from base64
        reconstructed_key = Ed25519PrivateKey.from_base64(base64_string)
        assert reconstructed_key.to_bytes() == original_key.to_bytes()
    
    def test_from_base64_invalid(self):
        """Test creating Ed25519 private key from invalid base64."""
        with pytest.raises(SuiValidationError, match="Invalid base64 string"):
            Ed25519PrivateKey.from_base64("invalid base64!!!")
        
        with pytest.raises(SuiValidationError, match="Base64 string must be a string"):
            Ed25519PrivateKey.from_base64(123)
    
    def test_public_key_derivation(self):
        """Test deriving public key from private key."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        assert isinstance(public_key, Ed25519PublicKey)
        assert public_key.scheme == SignatureScheme.ED25519
        assert len(public_key.to_bytes()) == 32
    
    def test_public_key_consistency(self):
        """Test that public key derivation is consistent."""
        private_key = Ed25519PrivateKey.generate()
        
        # Derive public key multiple times
        public_key1 = private_key.public_key()
        public_key2 = private_key.public_key()
        
        # Should be identical
        assert public_key1.to_bytes() == public_key2.to_bytes()
    
    def test_signing(self):
        """Test message signing with Ed25519 private key."""
        private_key = Ed25519PrivateKey.generate()
        message = b"Hello, Sui blockchain!"
        
        signature = private_key.sign(message)
        
        assert isinstance(signature, Signature)
        assert signature.scheme == SignatureScheme.ED25519
        assert len(signature.to_bytes()) == 64  # Ed25519 signature is 64 bytes
    
    def test_signing_invalid_message(self):
        """Test signing with invalid message type."""
        private_key = Ed25519PrivateKey.generate()
        
        with pytest.raises(SuiValidationError, match="Message must be bytes"):
            private_key.sign("not bytes")
    
    def test_signing_deterministic(self):
        """Test that signing the same message produces the same signature."""
        private_key = Ed25519PrivateKey.generate()
        message = b"Test message for deterministic signing"
        
        signature1 = private_key.sign(message)
        signature2 = private_key.sign(message)
        
        # Ed25519 signing should be deterministic
        assert signature1.to_bytes() == signature2.to_bytes()
    
    def test_serialization_hex(self):
        """Test private key hex serialization."""
        private_key = Ed25519PrivateKey.generate()
        hex_string = private_key.to_hex()
        
        # Should have 0x prefix and be 64 hex chars + 2 for prefix
        assert hex_string.startswith("0x")
        assert len(hex_string) == 66
        assert all(c in "0123456789abcdef" for c in hex_string[2:])
    
    def test_serialization_base64(self):
        """Test private key base64 serialization."""
        private_key = Ed25519PrivateKey.generate()
        base64_string = private_key.to_base64()
        
        # Should be valid base64 that decodes to 32 bytes
        decoded = base64.b64decode(base64_string)
        assert len(decoded) == 32
        assert decoded == private_key.to_bytes()
    
    def test_serialization_roundtrip(self):
        """Test that serialization/deserialization is lossless."""
        original_key = Ed25519PrivateKey.generate()
        
        # Test hex roundtrip
        hex_string = original_key.to_hex()
        hex_reconstructed = Ed25519PrivateKey.from_hex(hex_string)
        assert hex_reconstructed.to_bytes() == original_key.to_bytes()
        
        # Test base64 roundtrip
        base64_string = original_key.to_base64()
        base64_reconstructed = Ed25519PrivateKey.from_base64(base64_string)
        assert base64_reconstructed.to_bytes() == original_key.to_bytes()
        
        # Test bytes roundtrip
        key_bytes = original_key.to_bytes()
        bytes_reconstructed = Ed25519PrivateKey.from_bytes(key_bytes)
        assert bytes_reconstructed.to_bytes() == original_key.to_bytes()
    
    def test_factory_import(self):
        """Test importing private key via factory function."""
        original_key = Ed25519PrivateKey.generate()
        key_bytes = original_key.to_bytes()
        
        imported_key = import_private_key(key_bytes, SignatureScheme.ED25519)
        
        assert isinstance(imported_key, Ed25519PrivateKey)
        assert imported_key.to_bytes() == key_bytes
        assert imported_key.scheme == SignatureScheme.ED25519


class TestEd25519PublicKey:
    """Test cases for Ed25519 public key functionality."""
    
    def test_from_bytes_valid(self):
        """Test creating Ed25519 public key from valid bytes."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_bytes = public_key.to_bytes()
        
        reconstructed_key = Ed25519PublicKey.from_bytes(public_key_bytes)
        assert reconstructed_key.to_bytes() == public_key_bytes
        assert reconstructed_key.scheme == SignatureScheme.ED25519
    
    def test_from_bytes_invalid_length(self):
        """Test creating Ed25519 public key from invalid length bytes."""
        invalid_lengths = [0, 1, 16, 31, 33, 64]
        
        for length in invalid_lengths:
            key_bytes = secrets.token_bytes(length)
            with pytest.raises(SuiValidationError, match="must be 32 bytes"):
                Ed25519PublicKey.from_bytes(key_bytes)
    
    def test_from_bytes_invalid_type(self):
        """Test creating Ed25519 public key from non-bytes."""
        with pytest.raises(SuiValidationError, match="must be bytes"):
            Ed25519PublicKey.from_bytes("not bytes")
    
    def test_from_hex_valid(self):
        """Test creating Ed25519 public key from valid hex string."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        hex_string = public_key.to_hex()
        
        # Test with 0x prefix
        reconstructed_key = Ed25519PublicKey.from_hex(hex_string)
        assert reconstructed_key.to_bytes() == public_key.to_bytes()
        
        # Test without 0x prefix
        hex_no_prefix = hex_string[2:]
        reconstructed_key_no_prefix = Ed25519PublicKey.from_hex(hex_no_prefix)
        assert reconstructed_key_no_prefix.to_bytes() == public_key.to_bytes()
    
    def test_from_hex_invalid(self):
        """Test creating Ed25519 public key from invalid hex."""
        with pytest.raises(SuiValidationError, match="must be 64 characters"):
            Ed25519PublicKey.from_hex("0x" + "a" * 63)  # Too short
        
        with pytest.raises(SuiValidationError, match="Invalid hex string"):
            Ed25519PublicKey.from_hex("0x" + "g" * 64)  # Invalid hex
    
    def test_from_base64_valid(self):
        """Test creating Ed25519 public key from valid base64."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        base64_string = public_key.to_base64()
        
        reconstructed_key = Ed25519PublicKey.from_base64(base64_string)
        assert reconstructed_key.to_bytes() == public_key.to_bytes()
    
    def test_from_base64_invalid(self):
        """Test creating Ed25519 public key from invalid base64."""
        with pytest.raises(SuiValidationError, match="Invalid base64 string"):
            Ed25519PublicKey.from_base64("invalid base64!!!")
    
    def test_invalid_inputs_comprehensive(self):
        """Test comprehensive invalid input scenarios from TypeScript test suite."""
        
        # Test invalid length (33 bytes instead of 32)
        invalid_33_bytes = [3] + [0] * 32
        with pytest.raises(SuiValidationError, match="must be 32 bytes"):
            Ed25519PublicKey.from_bytes(bytes(invalid_33_bytes))
        
        # Test invalid hex string too long (33 bytes = 66 hex chars)
        invalid_hex_long = "0x" + "30" + "00" * 32  # 33 bytes
        with pytest.raises(SuiValidationError, match="must be 64 characters"):
            Ed25519PublicKey.from_hex(invalid_hex_long)
        
        # Test invalid hex string too short (31 bytes = 62 hex chars)
        invalid_hex_short = "0x" + "30" + "00" * 30  # 31 bytes
        with pytest.raises(SuiValidationError, match="must be 64 characters"):
            Ed25519PublicKey.from_hex(invalid_hex_short)
        
        # Test completely invalid formats
        with pytest.raises(SuiValidationError):
            Ed25519PublicKey.from_hex("12345")
        
        # Test integer input
        with pytest.raises(SuiValidationError):
            Ed25519PublicKey.from_hex(135693854574979916511997248057056142015550763280047535983739356259273198796800000)
    
    def test_signature_verification_valid(self):
        """Test valid signature verification."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        message = b"Test message for signature verification"
        
        signature = private_key.sign(message)
        is_valid = public_key.verify(message, signature)
        
        assert is_valid is True
    
    def test_signature_verification_invalid_message(self):
        """Test signature verification with wrong message."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        message1 = b"Original message"
        message2 = b"Different message"
        
        signature = private_key.sign(message1)
        is_valid = public_key.verify(message2, signature)
        
        assert is_valid is False
    
    def test_signature_verification_wrong_key(self):
        """Test signature verification with wrong public key."""
        private_key1 = Ed25519PrivateKey.generate()
        private_key2 = Ed25519PrivateKey.generate()
        public_key2 = private_key2.public_key()
        
        message = b"Test message"
        signature = private_key1.sign(message)
        is_valid = public_key2.verify(message, signature)
        
        assert is_valid is False
    
    def test_signature_verification_invalid_inputs(self):
        """Test signature verification with invalid inputs."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        message = b"Test message"
        signature = private_key.sign(message)
        
        # Invalid message type
        with pytest.raises(SuiValidationError, match="Message must be bytes"):
            public_key.verify("not bytes", signature)
        
        # Invalid signature type
        with pytest.raises(SuiValidationError, match="Signature must be a Signature instance"):
            public_key.verify(message, "not signature")
    
    def test_signature_verification_wrong_scheme(self):
        """Test signature verification with wrong signature scheme."""
        from sui_py import Secp256k1PrivateKey
        
        ed25519_private = Ed25519PrivateKey.generate()
        ed25519_public = ed25519_private.public_key()
        secp256k1_private = Secp256k1PrivateKey.generate()
        
        message = b"Test message"
        secp256k1_signature = secp256k1_private.sign(message)
        
        # Should raise validation error for scheme mismatch
        with pytest.raises(SuiValidationError, match="Signature scheme.*does not match"):
            ed25519_public.verify(message, secp256k1_signature)
    
    def test_sui_address_derivation(self):
        """Test Sui address derivation from Ed25519 public key."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        address = public_key.to_sui_address()
        
        assert isinstance(address, SuiAddress)
        assert str(address).startswith("0x")
        assert len(str(address)) == 66  # 0x + 64 hex chars
    
    def test_sui_address_consistency(self):
        """Test that address derivation is consistent."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        address1 = public_key.to_sui_address()
        address2 = public_key.to_sui_address()
        
        assert str(address1) == str(address2)
    
    def test_sui_address_uniqueness(self):
        """Test that different keys produce different addresses."""
        private_key1 = Ed25519PrivateKey.generate()
        private_key2 = Ed25519PrivateKey.generate()
        
        address1 = private_key1.public_key().to_sui_address()
        address2 = private_key2.public_key().to_sui_address()
        
        assert str(address1) != str(address2)
    
    def test_official_sui_cli_test_vectors_comprehensive(self):
        """Test against official Sui CLI test vectors for full cross-platform compatibility."""
        for i, test_vector in enumerate(SUI_CLI_TEST_VECTORS):
            # Create public key from raw base64
            public_key = Ed25519PublicKey.from_base64(test_vector["raw_public_key"])
            
            # Test 1: Basic key properties
            assert len(public_key.to_bytes()) == 32
            assert public_key.scheme == SignatureScheme.ED25519
            
            # Test 2: Raw key roundtrip
            assert public_key.to_base64() == test_vector["raw_public_key"]
            
            # Test 3: to_sui_public_key() method (NEW!)
            sui_public_key = public_key.to_sui_public_key()
            assert sui_public_key == test_vector["sui_public_key"], (
                f"Test vector {i}: Sui public key mismatch\n"
                f"Expected: {test_vector['sui_public_key']}\n"
                f"Got:      {sui_public_key}"
            )
            
            # Test 4: Address derivation (SHOULD NOW MATCH!)
            derived_address = public_key.to_sui_address()
            expected_address = test_vector["sui_address"]
            assert str(derived_address) == expected_address, (
                f"Test vector {i}: Address mismatch\n"
                f"Expected: {expected_address}\n"
                f"Got:      {str(derived_address)}"
            )
            
            print(f"✅ Test vector {i}: All tests passed!")
            print(f"   Raw public key: {test_vector['raw_public_key']}")
            print(f"   Sui public key: {sui_public_key}")  
            print(f"   Sui address:    {str(derived_address)}")
    
    def test_to_sui_public_key_method(self):
        """Test the to_sui_public_key method specifically."""
        # Generate a test key
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Get components
        raw_key_bytes = public_key.to_bytes()
        sui_bytes = public_key.to_sui_bytes()
        sui_public_key = public_key.to_sui_public_key()
        
        # Validate structure
        assert len(raw_key_bytes) == 32
        assert len(sui_bytes) == 33
        assert sui_bytes[0] == 0x00  # Ed25519 flag byte
        assert sui_bytes[1:] == raw_key_bytes
        
        # Validate base64 encoding
        import base64
        expected_sui_public_key = base64.b64encode(sui_bytes).decode('utf-8')
        assert sui_public_key == expected_sui_public_key
        
        # Test roundtrip via sui_bytes
        reconstructed_sui_bytes = base64.b64decode(sui_public_key)
        assert reconstructed_sui_bytes == sui_bytes
    
    def test_to_sui_bytes_method(self):
        """Test the to_sui_bytes helper method."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        sui_bytes = public_key.to_sui_bytes()
        raw_bytes = public_key.to_bytes()
        
        # Should be 33 bytes: flag + 32-byte key
        assert len(sui_bytes) == 33
        assert sui_bytes[0] == 0x00  # Ed25519 flag
        assert sui_bytes[1:] == raw_bytes
    
    def test_serialization_hex(self):
        """Test public key hex serialization."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        hex_string = public_key.to_hex()
        
        assert hex_string.startswith("0x")
        assert len(hex_string) == 66
        assert all(c in "0123456789abcdef" for c in hex_string[2:])
    
    def test_serialization_base64(self):
        """Test public key base64 serialization."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        base64_string = public_key.to_base64()
        
        decoded = base64.b64decode(base64_string)
        assert len(decoded) == 32
        assert decoded == public_key.to_bytes()
    
    def test_serialization_roundtrip(self):
        """Test that public key serialization/deserialization is lossless."""
        private_key = Ed25519PrivateKey.generate()
        original_public_key = private_key.public_key()
        
        # Test hex roundtrip
        hex_string = original_public_key.to_hex()
        hex_reconstructed = Ed25519PublicKey.from_hex(hex_string)
        assert hex_reconstructed.to_bytes() == original_public_key.to_bytes()
        
        # Test base64 roundtrip
        base64_string = original_public_key.to_base64()
        base64_reconstructed = Ed25519PublicKey.from_base64(base64_string)
        assert base64_reconstructed.to_bytes() == original_public_key.to_bytes()
        
        # Test bytes roundtrip
        key_bytes = original_public_key.to_bytes()
        bytes_reconstructed = Ed25519PublicKey.from_bytes(key_bytes)
        assert bytes_reconstructed.to_bytes() == original_public_key.to_bytes()


class TestEd25519Integration:
    """Integration tests for Ed25519 functionality."""
    
    def test_complete_key_lifecycle(self):
        """Test complete key generation, signing, and verification lifecycle."""
        # Generate key pair
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Verify schemes match
        assert private_key.scheme == public_key.scheme == SignatureScheme.ED25519
        
        # Test signing and verification
        messages = [
            b"",  # Empty message
            b"Hello, world!",
            b"x" * 1000,  # Long message
            bytes(range(256)),  # All byte values
        ]
        
        for message in messages:
            signature = private_key.sign(message)
            is_valid = public_key.verify(message, signature)
            assert is_valid is True
    
    def test_cross_serialization_compatibility(self):
        """Test that different serialization methods are compatible."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        message = b"Cross-serialization test message"
        
        # Create signature
        original_signature = private_key.sign(message)
        
        # Serialize and reconstruct private key in different ways
        private_hex = private_key.to_hex()
        private_b64 = private_key.to_base64()
        private_bytes = private_key.to_bytes()
        
        reconstructed_private_hex = Ed25519PrivateKey.from_hex(private_hex)
        reconstructed_private_b64 = Ed25519PrivateKey.from_base64(private_b64)
        reconstructed_private_bytes = Ed25519PrivateKey.from_bytes(private_bytes)
        
        # All reconstructed keys should produce same signatures
        sig_hex = reconstructed_private_hex.sign(message)
        sig_b64 = reconstructed_private_b64.sign(message)
        sig_bytes = reconstructed_private_bytes.sign(message)
        
        assert sig_hex.to_bytes() == original_signature.to_bytes()
        assert sig_b64.to_bytes() == original_signature.to_bytes()
        assert sig_bytes.to_bytes() == original_signature.to_bytes()
        
        # Serialize and reconstruct public key in different ways
        public_hex = public_key.to_hex()
        public_b64 = public_key.to_base64()
        public_bytes = public_key.to_bytes()
        
        reconstructed_public_hex = Ed25519PublicKey.from_hex(public_hex)
        reconstructed_public_b64 = Ed25519PublicKey.from_base64(public_b64)
        reconstructed_public_bytes = Ed25519PublicKey.from_bytes(public_bytes)
        
        # All reconstructed public keys should verify the signature
        assert reconstructed_public_hex.verify(message, original_signature)
        assert reconstructed_public_b64.verify(message, original_signature)
        assert reconstructed_public_bytes.verify(message, original_signature)
    
    def test_known_test_vector(self):
        """Test with known test vectors to ensure correctness."""
        # Use a known private key for deterministic testing
        known_private_hex = "0x" + "a" * 64  # Simple test pattern
        known_message = b"test message for known vector"
        
        # Create key from known hex
        private_key = Ed25519PrivateKey.from_hex(known_private_hex)
        public_key = private_key.public_key()
        
        # Sign and verify
        signature = private_key.sign(known_message)
        is_valid = public_key.verify(known_message, signature)
        assert is_valid is True
        
        # Ensure signature is deterministic
        signature2 = private_key.sign(known_message)
        assert signature.to_bytes() == signature2.to_bytes()
        
        # Verify address derivation is deterministic
        address1 = public_key.to_sui_address()
        address2 = public_key.to_sui_address()
        assert str(address1) == str(address2)
    
    def test_multiple_key_independence(self):
        """Test that multiple keys operate independently."""
        # Generate multiple key pairs
        keys = [Ed25519PrivateKey.generate() for _ in range(5)]
        public_keys = [key.public_key() for key in keys]
        message = b"Independence test message"
        
        # Create signatures
        signatures = [key.sign(message) for key in keys]
        
        # Each key should verify its own signature
        for i, (public_key, signature) in enumerate(zip(public_keys, signatures)):
            assert public_key.verify(message, signature)
        
        # Keys should not verify other signatures
        for i, public_key in enumerate(public_keys):
            for j, signature in enumerate(signatures):
                if i != j:
                    assert not public_key.verify(message, signature)
    
    def test_edge_case_messages(self):
        """Test signing and verification with edge case messages."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        edge_cases = [
            b"",  # Empty
            b"\x00",  # Single null byte
            b"\x00" * 1000,  # Many null bytes
            b"\xff" * 1000,  # Many 0xFF bytes
            bytes(range(256)) * 10,  # All byte values repeated
            b"Unicode: \xe2\x9c\x93\xf0\x9f\x8e\x89",  # Unicode bytes
        ]
        
        for message in edge_cases:
            signature = private_key.sign(message)
            assert public_key.verify(message, signature)
            
            # Verify wrong message fails
            wrong_message = message + b"extra"
            assert not public_key.verify(wrong_message, signature)


if __name__ == "__main__":
    pytest.main([__file__]) 