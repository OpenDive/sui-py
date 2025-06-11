#!/usr/bin/env python3
"""
Simple test script to verify Account implementation.
"""

from sui_py.accounts import Account
from sui_py.crypto import SignatureScheme

def test_accounts():
    print('Testing Account creation...')

    # Test Ed25519
    ed25519_account = Account.generate(SignatureScheme.ED25519)
    print(f'Ed25519 Account: {ed25519_account.address}')
    print(f'Scheme: {ed25519_account.scheme}')

    # Test Secp256k1  
    secp256k1_account = Account.generate(SignatureScheme.SECP256K1)
    print(f'Secp256k1 Account: {secp256k1_account.address}') 
    print(f'Scheme: {secp256k1_account.scheme}')

    # Test signing and verification
    message = b'Hello, Sui!'
    signature = ed25519_account.sign(message)
    is_valid = ed25519_account.verify(message, signature)
    print(f'Signature valid: {is_valid}')

    # Test serialization
    account_data = ed25519_account.to_dict()
    print(f'Account data keys: {list(account_data.keys())}')

    # Test deserialization
    restored_account = Account.from_dict(account_data)
    print(f'Restored account matches: {restored_account.address == ed25519_account.address}')

    # Test different creation methods
    private_key_hex = ed25519_account.export_private_key_hex()
    hex_account = Account.from_hex(private_key_hex, SignatureScheme.ED25519)
    print(f'Hex import matches: {hex_account.address == ed25519_account.address}')

    print('All tests passed! ✅')

if __name__ == "__main__":
    test_accounts() 