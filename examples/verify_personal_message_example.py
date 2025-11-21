"""
Example demonstrating personal message signing and verification.

This example shows how to use the new verifyPersonalMessage functionality
that matches the TypeScript SDK's implementation.
"""

from sui_py import (
    Account,
    SignatureScheme,
    Signature,
)


def main():
    print("🔐 Personal Message Signing and Verification Example")
    print("=" * 60)
    
    # Create an account
    account = Account.generate(SignatureScheme.ED25519)
    print(f"\n✅ Generated account: {account.address}")
    
    # Create a personal message
    message = b"Hello, Sui blockchain! This is a personal message."
    print(f"\n📝 Message to sign: {message.decode('utf-8')}")
    
    # Sign the personal message
    signature_b64 = account.sign_personal_message(message)
    print(f"\n✍️  Signed message")
    print(f"   Signature (base64): {signature_b64[:60]}...")
    
    # Parse the signature back
    signature = Signature.from_sui_base64(signature_b64)
    print(f"   Signature scheme: {signature.scheme}")
    
    # Verify the signature using the public key
    is_valid = account.public_key.verify_personal_message(message, signature)
    print(f"\n✅ Signature verification: {is_valid}")
    
    # Try verifying with a wrong message (should fail)
    wrong_message = b"This is a different message"
    is_valid_wrong = account.public_key.verify_personal_message(wrong_message, signature)
    print(f"\n❌ Wrong message verification: {is_valid_wrong} (expected False)")
    
    # Demonstrate with different schemes
    print("\n" + "=" * 60)
    print("🔄 Testing with different signature schemes")
    print("=" * 60)
    
    for scheme in [SignatureScheme.ED25519, SignatureScheme.SECP256K1]:
        account = Account.generate(scheme)
        sig_b64 = account.sign_personal_message(message)
        sig = Signature.from_sui_base64(sig_b64)
        is_valid = account.public_key.verify_personal_message(message, sig)
        
        print(f"\n{scheme.value}:")
        print(f"  Address: {account.address}")
        print(f"  Valid: {is_valid}")
    
    print("\n" + "=" * 60)
    print("✨ All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

