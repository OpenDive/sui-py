"""
Comprehensive example of cryptographic operations with SuiPy.

This example demonstrates:
- Key generation and management (Ed25519 and Secp256k1)
- Message signing and verification  
- Sui address derivation
- Signature serialization and reconstruction
- Multi-scheme operations and validation
- Error handling and validation
"""

from sui_py import (
    SignatureScheme, 
    create_private_key, 
    import_private_key,
    Ed25519PrivateKey, 
    Ed25519PublicKey,
    Secp256k1PrivateKey,
    Secp256k1PublicKey,
    Signature,
    SuiValidationError
)


def main():
    print("🔐 SuiPy Cryptographic Operations Example")
    print("=" * 50)
    
    # 1. Key Generation (Multiple Schemes)
    print("\n1. Key Generation (Multiple Schemes)")
    print("-" * 38)
    
    # Generate Ed25519 key pair
    ed25519_private_key = create_private_key(SignatureScheme.ED25519)
    ed25519_public_key = ed25519_private_key.public_key()
    
    # Generate Secp256k1 key pair
    secp256k1_private_key = create_private_key(SignatureScheme.SECP256K1)
    secp256k1_public_key = secp256k1_private_key.public_key()
    
    print(f"✅ Generated Ed25519 key pair (scheme: {ed25519_private_key.scheme})")
    print(f"✅ Generated Secp256k1 key pair (scheme: {secp256k1_private_key.scheme})")
    
    # 2. Address Derivation Comparison
    print("\n2. Sui Address Derivation Comparison")
    print("-" * 37)
    
    ed25519_address = ed25519_public_key.to_sui_address()
    secp256k1_address = secp256k1_public_key.to_sui_address()
    
    print(f"✅ Ed25519 address:  {ed25519_address}")
    print(f"✅ Secp256k1 address: {secp256k1_address}")
    print(f"✅ Different addresses: {ed25519_address != secp256k1_address}")
    
    # 3. Multi-Scheme Signing
    print("\n3. Multi-Scheme Message Signing")
    print("-" * 31)
    
    message = b"Hello, Sui blockchain! Multi-scheme test message."
    
    ed25519_signature = ed25519_private_key.sign(message)
    secp256k1_signature = secp256k1_private_key.sign(message)
    
    print(f"✅ Ed25519 signature scheme: {ed25519_signature.scheme}")
    print(f"✅ Secp256k1 signature scheme: {secp256k1_signature.scheme}")
    print(f"✅ Ed25519 signature length: {len(ed25519_signature.to_bytes())} bytes")
    print(f"✅ Secp256k1 signature length: {len(secp256k1_signature.to_bytes())} bytes")
    
    # 4. Signature Verification
    print("\n4. Signature Verification")
    print("-" * 24)
    
    ed25519_valid = ed25519_public_key.verify(message, ed25519_signature)
    secp256k1_valid = secp256k1_public_key.verify(message, secp256k1_signature)
    
    print(f"✅ Ed25519 self-verification: {ed25519_valid}")
    print(f"✅ Secp256k1 self-verification: {secp256k1_valid}")
    
    # Test wrong message verification
    wrong_message = b"This is a different message"
    ed25519_invalid = ed25519_public_key.verify(wrong_message, ed25519_signature)
    secp256k1_invalid = secp256k1_public_key.verify(wrong_message, secp256k1_signature)
    
    print(f"✅ Ed25519 wrong message: {ed25519_invalid} (expected False)")
    print(f"✅ Secp256k1 wrong message: {secp256k1_invalid} (expected False)")
    
    # 5. Scheme Security Validation
    print("\n5. Scheme Security Validation")
    print("-" * 29)
    
    try:
        # Try to verify Ed25519 signature with Secp256k1 key
        ed25519_public_key.verify(message, secp256k1_signature)
        print("❌ Should not reach here")
    except SuiValidationError:
        print("✅ Ed25519 key correctly rejects Secp256k1 signature")
    
    try:
        # Try to verify Secp256k1 signature with Ed25519 key
        secp256k1_public_key.verify(message, ed25519_signature)
        print("❌ Should not reach here")
    except SuiValidationError:
        print("✅ Secp256k1 key correctly rejects Ed25519 signature")
    
    # 6. Key Serialization (Both Schemes)
    print("\n6. Key Serialization (Both Schemes)")
    print("-" * 35)
    
    # Ed25519 serialization
    ed25519_private_hex = ed25519_private_key.to_hex()
    ed25519_public_hex = ed25519_public_key.to_hex()
    
    # Secp256k1 serialization  
    secp256k1_private_hex = secp256k1_private_key.to_hex()
    secp256k1_public_hex = secp256k1_public_key.to_hex()
    
    print(f"✅ Ed25519 private key: {ed25519_private_hex[:20]}...")
    print(f"✅ Ed25519 public key:  {ed25519_public_hex[:20]}...")
    print(f"✅ Secp256k1 private key: {secp256k1_private_hex[:20]}...")
    print(f"✅ Secp256k1 public key:  {secp256k1_public_hex[:20]}...")
    
    # 7. Key Import and Reconstruction
    print("\n7. Key Import and Reconstruction")
    print("-" * 31)
    
    # Import Ed25519 keys
    imported_ed25519_private = Ed25519PrivateKey.from_hex(ed25519_private_hex)
    imported_ed25519_public = Ed25519PublicKey.from_hex(ed25519_public_hex)
    
    # Import Secp256k1 keys
    imported_secp256k1_private = Secp256k1PrivateKey.from_hex(secp256k1_private_hex)
    imported_secp256k1_public = Secp256k1PublicKey.from_hex(secp256k1_public_hex)
    
    # Verify imported keys work
    ed25519_imported_sig = imported_ed25519_private.sign(message)
    secp256k1_imported_sig = imported_secp256k1_private.sign(message)
    
    ed25519_imported_verify = imported_ed25519_public.verify(message, ed25519_imported_sig)
    secp256k1_imported_verify = imported_secp256k1_public.verify(message, secp256k1_imported_sig)
    
    print(f"✅ Ed25519 imported key verification: {ed25519_imported_verify}")
    print(f"✅ Secp256k1 imported key verification: {secp256k1_imported_verify}")
    
    # Verify addresses match
    ed25519_imported_addr = imported_ed25519_public.to_sui_address()
    secp256k1_imported_addr = imported_secp256k1_public.to_sui_address()
    
    print(f"✅ Ed25519 addresses match: {ed25519_address == ed25519_imported_addr}")
    print(f"✅ Secp256k1 addresses match: {secp256k1_address == secp256k1_imported_addr}")
    
    # 8. Signature Serialization
    print("\n8. Signature Serialization")
    print("-" * 26)
    
    ed25519_sig_hex = ed25519_signature.to_hex()
    secp256k1_sig_hex = secp256k1_signature.to_hex()
    
    # Reconstruct signatures
    ed25519_reconstructed = Signature.from_hex(ed25519_sig_hex, SignatureScheme.ED25519)
    secp256k1_reconstructed = Signature.from_hex(secp256k1_sig_hex, SignatureScheme.SECP256K1)
    
    print(f"✅ Ed25519 signature reconstructed: {ed25519_signature == ed25519_reconstructed}")
    print(f"✅ Secp256k1 signature reconstructed: {secp256k1_signature == secp256k1_reconstructed}")
    
    # Verify reconstructed signatures work
    ed25519_reconstructed_verify = ed25519_public_key.verify(message, ed25519_reconstructed)
    secp256k1_reconstructed_verify = secp256k1_public_key.verify(message, secp256k1_reconstructed)
    
    print(f"✅ Ed25519 reconstructed verification: {ed25519_reconstructed_verify}")
    print(f"✅ Secp256k1 reconstructed verification: {secp256k1_reconstructed_verify}")
    
    # 9. Factory Function Testing
    print("\n9. Factory Function Testing")
    print("-" * 27)
    
    # Test factory functions with both schemes
    factory_ed25519 = create_private_key(SignatureScheme.ED25519)
    factory_secp256k1 = create_private_key(SignatureScheme.SECP256K1)
    
    print(f"✅ Factory Ed25519 scheme: {factory_ed25519.scheme}")
    print(f"✅ Factory Secp256k1 scheme: {factory_secp256k1.scheme}")
    
    # Test import factory function
    imported_factory_ed25519 = import_private_key(
        ed25519_private_key.to_bytes(), 
        SignatureScheme.ED25519
    )
    imported_factory_secp256k1 = import_private_key(
        secp256k1_private_key.to_bytes(),
        SignatureScheme.SECP256K1
    )
    
    print(f"✅ Import factory Ed25519 works: {imported_factory_ed25519.scheme}")
    print(f"✅ Import factory Secp256k1 works: {imported_factory_secp256k1.scheme}")
    
    # 10. Error Handling Examples
    print("\n10. Error Handling Examples")
    print("-" * 28)
    
    try:
        # Try unsupported scheme
        create_private_key(SignatureScheme.SECP256R1)
    except NotImplementedError:
        print("✅ Correctly rejects unsupported Secp256r1")
    
    try:
        # Try invalid Secp256k1 private key (all zeros)
        Secp256k1PrivateKey.from_bytes(b'\x00' * 32)
    except SuiValidationError:
        print("✅ Correctly rejects zero private key")
    
    try:
        # Try invalid signature scheme mismatch  
        wrong_scheme_sig = Signature(ed25519_signature.to_bytes(), SignatureScheme.SECP256K1)
        secp256k1_public_key.verify(message, wrong_scheme_sig)
    except SuiValidationError:
        print("✅ Correctly detects signature scheme mismatch")
    
    print("\n🎉 All multi-scheme cryptographic operations completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main() 