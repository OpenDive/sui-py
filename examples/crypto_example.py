"""
Comprehensive example of cryptographic operations with SuiPy.

This example demonstrates:
- Key generation and management
- Message signing and verification  
- Sui address derivation
- Signature serialization and reconstruction
- Error handling and validation
"""

from sui_py import (
    SignatureScheme, 
    create_private_key, 
    import_private_key,
    Ed25519PrivateKey, 
    Ed25519PublicKey,
    Signature,
    SuiValidationError
)


def main():
    print("🔐 SuiPy Cryptographic Operations Example")
    print("=" * 50)
    
    # 1. Key Generation
    print("\n1. Key Generation")
    print("-" * 20)
    
    # Generate a new Ed25519 key pair
    private_key = create_private_key(SignatureScheme.ED25519)
    public_key = private_key.public_key()
    
    print(f"✅ Generated Ed25519 key pair")
    print(f"Private key scheme: {private_key.scheme}")
    print(f"Public key scheme: {public_key.scheme}")
    
    # 2. Address Derivation
    print("\n2. Sui Address Derivation")
    print("-" * 25)
    
    address = public_key.to_sui_address()
    print(f"✅ Derived Sui address: {address}")
    
    # 3. Message Signing
    print("\n3. Message Signing and Verification")
    print("-" * 35)
    
    message = b"Hello, Sui blockchain! This is a test message."
    signature = private_key.sign(message)
    
    print(f"✅ Signed message: {message.decode()}")
    print(f"Signature scheme: {signature.scheme}")
    print(f"Signature length: {len(signature.to_bytes())} bytes")
    
    # 4. Signature Verification
    is_valid = public_key.verify(message, signature)
    print(f"✅ Signature verification: {is_valid}")
    
    # Verify with wrong message (should fail)
    wrong_message = b"This is a different message"
    is_invalid = public_key.verify(wrong_message, signature)
    print(f"✅ Wrong message verification: {is_invalid} (expected False)")
    
    # 5. Key Serialization and Import
    print("\n5. Key Serialization and Import")
    print("-" * 32)
    
    # Export private key
    private_key_hex = private_key.to_hex()
    private_key_bytes = private_key.to_bytes()
    
    print(f"✅ Private key exported")
    print(f"Hex format: {private_key_hex}")
    print(f"Bytes length: {len(private_key_bytes)} bytes")
    
    # Import private key from hex
    imported_key = Ed25519PrivateKey.from_hex(private_key_hex)
    print(f"✅ Private key imported from hex")
    
    # Import using factory function
    imported_key2 = import_private_key(private_key_bytes, SignatureScheme.ED25519)
    print(f"✅ Private key imported using factory function")
    
    # Verify imported keys work the same
    imported_signature = imported_key.sign(message)
    imported_verification = imported_key.public_key().verify(message, imported_signature)
    print(f"✅ Imported key verification: {imported_verification}")
    
    # 6. Public Key Operations
    print("\n6. Public Key Operations")
    print("-" * 24)
    
    # Export public key
    public_key_hex = public_key.to_hex()
    public_key_bytes = public_key.to_bytes()
    
    print(f"✅ Public key exported")
    print(f"Hex format: {public_key_hex}")
    print(f"Bytes length: {len(public_key_bytes)} bytes")
    
    # Import public key
    imported_public_key = Ed25519PublicKey.from_hex(public_key_hex)
    imported_address = imported_public_key.to_sui_address()
    
    print(f"✅ Public key imported from hex")
    print(f"Addresses match: {address == imported_address}")
    
    # 7. Signature Serialization
    print("\n7. Signature Serialization")
    print("-" * 26)
    
    signature_hex = signature.to_hex()
    signature_bytes = signature.to_bytes()
    
    print(f"✅ Signature exported")
    print(f"Hex format: {signature_hex}")
    print(f"Bytes length: {len(signature_bytes)} bytes")
    
    # Reconstruct signature
    reconstructed_signature = Signature.from_hex(signature_hex, SignatureScheme.ED25519)
    signatures_equal = signature == reconstructed_signature
    
    print(f"✅ Signature reconstructed from hex")
    print(f"Signatures equal: {signatures_equal}")
    
    # Verify reconstructed signature works
    reconstructed_verification = public_key.verify(message, reconstructed_signature)
    print(f"✅ Reconstructed signature verification: {reconstructed_verification}")
    
    # 8. Error Handling Examples
    print("\n8. Error Handling Examples")
    print("-" * 27)
    
    try:
        # Try to import invalid hex
        Ed25519PrivateKey.from_hex("invalid_hex")
    except SuiValidationError as e:
        print(f"✅ Caught invalid hex error: {str(e)[:50]}...")
    
    try:
        # Try to import wrong length private key
        Ed25519PrivateKey.from_bytes(b"too_short")
    except SuiValidationError as e:
        print(f"✅ Caught wrong length error: {str(e)[:50]}...")
    
    try:
        # Try to verify with mismatched signature scheme
        wrong_scheme_sig = Signature(signature.to_bytes(), SignatureScheme.SECP256K1)
        public_key.verify(message, wrong_scheme_sig)
    except SuiValidationError as e:
        print(f"✅ Caught scheme mismatch error: {str(e)[:50]}...")
    
    # 9. Multiple Key Pairs
    print("\n9. Multiple Key Pairs")
    print("-" * 20)
    
    # Generate multiple key pairs
    key_pairs = []
    for i in range(3):
        priv_key = create_private_key(SignatureScheme.ED25519)
        pub_key = priv_key.public_key()
        addr = pub_key.to_sui_address()
        key_pairs.append((priv_key, pub_key, addr))
        print(f"✅ Key pair {i+1}: {str(addr)[:20]}...")
    
    # Cross-verification (should fail)
    test_message = b"Cross verification test"
    sig1 = key_pairs[0][0].sign(test_message)
    cross_verify = key_pairs[1][1].verify(test_message, sig1)
    print(f"✅ Cross-verification test: {cross_verify} (expected False)")
    
    print("\n🎉 All cryptographic operations completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main() 