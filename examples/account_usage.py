#!/usr/bin/env python3
"""
Comprehensive example of Account usage in SuiPy.

This example demonstrates:
- Creating accounts with different signature schemes
- Importing/exporting accounts
- Signing and verification
- Integration with existing crypto primitives
- Account serialization for storage
"""

from sui_py import (
    Account, AbstractAccount, SignatureScheme,
    Ed25519PrivateKey, Secp256k1PrivateKey
)


def main():
    print("🔐 SuiPy Account Usage Examples")
    print("=" * 50)
    
    # 1. Generate new accounts for each supported scheme
    print("\n1️⃣  Generating new accounts...")
    
    ed25519_account = Account.generate(SignatureScheme.ED25519)
    secp256k1_account = Account.generate(SignatureScheme.SECP256K1)
    
    print(f"Ed25519 Account:   {ed25519_account.address}")
    print(f"Secp256k1 Account: {secp256k1_account.address}")
    
    # 2. Create account from existing private key
    print("\n2️⃣  Creating account from existing private key...")
    
    existing_key = Ed25519PrivateKey.generate()
    account_from_key = Account.from_private_key(existing_key)
    
    # Verify they derive the same address
    direct_address = existing_key.public_key().to_sui_address()
    print(f"Account from key: {account_from_key.address}")
    print(f"Direct address:   {direct_address}")
    print(f"✅ Addresses match: {account_from_key.address == direct_address}")
    
    # 3. Import account from hex string
    print("\n3️⃣  Importing account from hex...")
    
    private_key_hex = ed25519_account.export_private_key_hex()
    imported_account = Account.from_hex(private_key_hex, SignatureScheme.ED25519)
    
    print(f"Original:  {ed25519_account.address}")
    print(f"Imported:  {imported_account.address}")
    print(f"✅ Import successful: {ed25519_account.address == imported_account.address}")
    
    # 4. Sign and verify messages
    print("\n4️⃣  Signing and verification...")
    
    message = b"Hello, Sui blockchain!"
    
    # Sign with different accounts
    ed25519_signature = ed25519_account.sign(message)
    secp256k1_signature = secp256k1_account.sign(message)
    
    # Verify signatures
    ed25519_valid = ed25519_account.verify(message, ed25519_signature)
    secp256k1_valid = secp256k1_account.verify(message, secp256k1_signature)
    
    print(f"Ed25519 signature valid:   ✅ {ed25519_valid}")
    print(f"Secp256k1 signature valid: ✅ {secp256k1_valid}")
    
    # Cross-verification (should fail)
    try:
        cross_valid = ed25519_account.verify(message, secp256k1_signature)
        print(f"Cross-verification fails:  ❌ False (unexpected)")
    except Exception:
        print(f"Cross-verification fails:  ✅ True (expected exception)")
    
    # 5. Account serialization for storage
    print("\n5️⃣  Account serialization...")
    
    account_data = ed25519_account.to_dict()
    print(f"Serialized keys: {list(account_data.keys())}")
    print(f"Scheme: {account_data['scheme']}")
    print(f"Address: {account_data['address']}")
    
    # Restore from serialized data
    restored_account = Account.from_dict(account_data)
    print(f"✅ Restoration successful: {restored_account.address == ed25519_account.address}")
    
    # 6. Different export formats
    print("\n6️⃣  Key export formats...")
    
    print(f"Private key (hex):    {ed25519_account.export_private_key_hex()[:20]}...")
    print(f"Private key (base64): {ed25519_account.export_private_key_base64()[:20]}...")
    print(f"Public key (hex):     {ed25519_account.export_public_key_hex()[:20]}...")
    print(f"Public key (base64):  {ed25519_account.export_public_key_base64()[:20]}...")
    
    # 7. Polymorphic usage
    print("\n7️⃣  Polymorphic account usage...")
    
    def demonstrate_account(account: AbstractAccount):
        """Function that works with any account type."""
        print(f"  Account scheme: {account.scheme}")
        print(f"  Account address: {account.address}")
        
        # Sign a test message
        test_msg = b"Polymorphic test"
        signature = account.sign(test_msg)
        is_valid = account.verify(test_msg, signature)
        print(f"  Signature valid: ✅ {is_valid}")
    
    print("Demonstrating polymorphic usage:")
    demonstrate_account(ed25519_account)
    demonstrate_account(secp256k1_account)
    
    # 8. Future HD Wallet integration preview
    print("\n8️⃣  Future HD Wallet integration preview...")
    print("When HD Wallets are implemented, they will manage multiple accounts:")
    print("  hd_wallet = HDWallet.from_mnemonic('word1 word2 ...')")
    print("  account_0 = hd_wallet.derive_account(0)  # Returns an Account")
    print("  account_1 = hd_wallet.derive_account(1)  # Returns another Account")
    print("  # Each account is a complete Account instance")
    
    print("\n🎉 All examples completed successfully!")


if __name__ == "__main__":
    main() 