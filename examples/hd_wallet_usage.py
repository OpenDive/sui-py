#!/usr/bin/env python3
"""
Comprehensive example of HD Wallet usage in SuiPy.

This example demonstrates:
- Creating HD wallets from mnemonics and generating new ones
- Deriving multiple accounts with different signature schemes
- Account management and caching
- Derivation path utilities
- Wallet serialization and restoration
- Integration with Account abstraction
"""

from sui_py import (
    HDWallet, Account, SignatureScheme,
    DerivationPath, SuiDerivationPath,
    WalletError, InvalidMnemonicError
)


def main():
    print("🏦 SuiPy HD Wallet Usage Examples")
    print("=" * 50)
    
    # 1. Generate new HD wallet
    print("\n1️⃣  Generating new HD wallet...")
    
    wallet = HDWallet.generate(word_count=12)
    print(f"Generated 12-word mnemonic: {wallet.mnemonic[:20]}...")
    print(f"Wallet: {wallet}")
    
    # Generate with different word counts
    wallet_24 = HDWallet.generate(word_count=24)
    print(f"Generated 24-word mnemonic: {wallet_24.mnemonic[:30]}...")
    
    # 2. Restore wallet from mnemonic
    print("\n2️⃣  Restoring wallet from mnemonic...")
    
    # Use the generated wallet's mnemonic
    test_mnemonic = wallet.mnemonic
    restored_wallet = HDWallet.from_mnemonic(test_mnemonic)
    print(f"Restored wallet: {restored_wallet}")
    print(f"Mnemonics match: {wallet.mnemonic == restored_wallet.mnemonic}")
    
    # 3. Derive accounts with different schemes
    print("\n3️⃣  Deriving accounts with different signature schemes...")
    
    # Derive Ed25519 accounts
    ed25519_account_0 = wallet.derive_account(0, SignatureScheme.ED25519)
    ed25519_account_1 = wallet.derive_account(1, SignatureScheme.ED25519)
    
    # Derive Secp256k1 accounts
    secp256k1_account_0 = wallet.derive_account(0, SignatureScheme.SECP256K1)
    secp256k1_account_1 = wallet.derive_account(1, SignatureScheme.SECP256K1)
    
    print(f"Ed25519 Account 0:   {ed25519_account_0.address}")
    print(f"Ed25519 Account 1:   {ed25519_account_1.address}")
    print(f"Secp256k1 Account 0: {secp256k1_account_0.address}")
    print(f"Secp256k1 Account 1: {secp256k1_account_1.address}")
    
    # Verify different schemes produce different addresses for same index
    print(f"Same index, different schemes produce different addresses: {ed25519_account_0.address != secp256k1_account_0.address}")
    
    # 4. Derivation path utilities
    print("\n4️⃣  Derivation path utilities...")
    
    # Standard Sui paths
    standard_path_0 = SuiDerivationPath.standard_account(0)
    standard_path_5 = SuiDerivationPath.standard_account(5)
    
    print(f"Standard path for account 0: {standard_path_0}")
    print(f"Standard path for account 5: {standard_path_5}")
    
    # Custom paths
    custom_path = SuiDerivationPath.custom_account(purpose=44, account=2, change=0, address_index=3)
    print(f"Custom path: {custom_path}")
    
    # Derive account at custom path
    custom_account = wallet.derive_account_at_path(custom_path, SignatureScheme.ED25519)
    print(f"Custom path account: {custom_account.address}")
    
    # 5. Account management
    print("\n5️⃣  Account management...")
    
    # List all cached accounts
    all_accounts = wallet.list_accounts()
    print(f"Total cached accounts: {len(all_accounts)}")
    
    for i, account in enumerate(all_accounts):
        print(f"  Account {i}: {account.scheme.value} - {account.address}")
    
    # Add new account with next available index
    new_account = wallet.add_account(SignatureScheme.ED25519)
    print(f"Added new Ed25519 account: {new_account.address}")
    
    # 6. Deterministic verification
    print("\n6️⃣  Deterministic verification...")
    
    # Create another wallet with same mnemonic
    wallet2 = HDWallet.from_mnemonic(test_mnemonic)
    
    # Derive same accounts
    wallet2_account_0 = wallet2.derive_account(0, SignatureScheme.ED25519)
    wallet2_account_1 = wallet2.derive_account(0, SignatureScheme.SECP256K1)
    
    print(f"Wallet 1 Ed25519 Account 0:  {ed25519_account_0.address}")
    print(f"Wallet 2 Ed25519 Account 0:  {wallet2_account_0.address}")
    print(f"Deterministic Ed25519: {ed25519_account_0.address == wallet2_account_0.address}")
    
    print(f"Wallet 1 Secp256k1 Account 0: {secp256k1_account_0.address}")
    print(f"Wallet 2 Secp256k1 Account 0: {wallet2_account_1.address}")
    print(f"Deterministic Secp256k1: {secp256k1_account_0.address == wallet2_account_1.address}")
    
    # 7. Account functionality integration
    print("\n7️⃣  Account functionality integration...")
    
    # Each derived account is a full Account instance
    test_account = wallet.derive_account(0, SignatureScheme.ED25519)
    message = b"HD Wallet test message"
    
    # Sign and verify with derived account
    signature = test_account.sign(message)
    is_valid = test_account.verify(message, signature)
    print(f"HD-derived account signing works: ✅ {is_valid}")
    
    # Export account details
    account_data = test_account.to_dict()
    print(f"Account scheme: {account_data['scheme']}")
    print(f"Account address: {account_data['address']}")
    
    # 8. Wallet serialization
    print("\n8️⃣  Wallet serialization...")
    
    # Export wallet data
    wallet_data = wallet.export_wallet_data()
    print(f"Wallet data keys: {list(wallet_data.keys())}")
    print(f"Exported accounts: {len(wallet_data['accounts'])}")
    print(f"Wallet version: {wallet_data['version']}")
    
    # Restore from exported data
    restored_from_data = HDWallet.from_wallet_data(wallet_data)
    print(f"Restored wallet: {restored_from_data}")
    
    # Verify restoration worked
    restored_account = restored_from_data.get_account(0, SignatureScheme.ED25519)
    original_account = wallet.get_account(0, SignatureScheme.ED25519)
    print(f"Restoration successful: {restored_account.address == original_account.address}")
    
    # 9. Mnemonic validation
    print("\n9️⃣  Mnemonic validation...")
    
    valid_mnemonic = wallet.mnemonic
    invalid_mnemonic = "invalid mnemonic phrase that should fail"
    
    print(f"Valid mnemonic check: ✅ {HDWallet.validate_mnemonic(valid_mnemonic)}")
    print(f"Invalid mnemonic check: ❌ {HDWallet.validate_mnemonic(invalid_mnemonic)}")
    
    # Test error handling
    try:
        HDWallet.from_mnemonic(invalid_mnemonic)
        print("❌ Should not reach here")
    except InvalidMnemonicError:
        print("✅ Correctly rejects invalid mnemonic")
    
    # 10. Advanced derivation path features
    print("\n🔟  Advanced derivation path features...")
    
    # Create custom derivation path
    custom_path = DerivationPath.from_components([44, 784, 0, 0, 10], hardened=[True, True, True, True, True])
    print(f"Custom path: {custom_path}")
    print(f"Path components: {custom_path.components}")
    print(f"Hardened components: {custom_path.hardened_components}")
    
    # Append to path
    extended_path = custom_path.append(5, hardened=True)
    print(f"Extended path: {extended_path}")
    
    # Validate Sui paths
    sui_valid = SuiDerivationPath.validate_sui_path(standard_path_0)
    bitcoin_path = DerivationPath("m/44'/0'/0'/0/0")
    bitcoin_valid = SuiDerivationPath.validate_sui_path(bitcoin_path)
    
    print(f"Sui path validation: ✅ {sui_valid}")
    print(f"Bitcoin path validation: ❌ {bitcoin_valid}")
    
    # 11. Multiple wallet management
    print("\n1️⃣1️⃣  Multiple wallet management...")
    
    # Create multiple wallets
    wallet_a = HDWallet.generate(12)
    wallet_b = HDWallet.generate(12)
    
    # Derive same account index but different wallets
    account_a = wallet_a.derive_account(0, SignatureScheme.ED25519)
    account_b = wallet_b.derive_account(0, SignatureScheme.ED25519)
    
    print(f"Wallet A account 0: {account_a.address}")
    print(f"Wallet B account 0: {account_b.address}")
    print(f"Different wallets produce different accounts: {account_a.address != account_b.address}")
    
    # But same wallet produces same accounts
    account_a2 = wallet_a.derive_account(0, SignatureScheme.ED25519)
    print(f"Same wallet, same account: {account_a.address == account_a2.address}")
    
    print("\n🎉 All HD Wallet examples completed successfully!")
    print("=" * 50)
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   • Generated wallets: 4")
    print(f"   • Total accounts derived: {len(wallet.list_accounts())}")
    print(f"   • Signature schemes tested: Ed25519, Secp256k1")
    print(f"   • Derivation paths tested: Standard, Custom")
    print(f"   • Features demonstrated: Generation, Restoration, Serialization")


if __name__ == "__main__":
    main() 