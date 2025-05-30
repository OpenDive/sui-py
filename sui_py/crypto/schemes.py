"""
Signature scheme definitions for Sui blockchain cryptography.
"""

from enum import Enum


class SignatureScheme(Enum):
    """
    Supported signature schemes on the Sui blockchain.
    
    Each scheme has different characteristics:
    - ED25519: Fast verification, 32-byte keys, 64-byte signatures
    - SECP256K1: Same curve as Bitcoin/Ethereum, 32-byte keys, ~72-byte signatures  
    - SECP256R1: NIST P-256 curve, 32-byte keys, ~72-byte signatures
    """
    ED25519 = "ED25519"
    SECP256K1 = "SECP256K1" 
    SECP256R1 = "SECP256R1"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def flag_byte(self) -> int:
        """
        Get the Sui flag byte for this signature scheme.
        
        These flags are used in Sui address derivation and signature serialization.
        """
        if self == SignatureScheme.ED25519:
            return 0x00
        elif self == SignatureScheme.SECP256K1:
            return 0x01
        elif self == SignatureScheme.SECP256R1:
            return 0x02
        else:
            raise ValueError(f"Unknown signature scheme: {self}")
    
    @classmethod
    def from_flag_byte(cls, flag: int) -> "SignatureScheme":
        """
        Create a SignatureScheme from a Sui flag byte.
        
        Args:
            flag: The flag byte (0x00, 0x01, or 0x02)
            
        Returns:
            The corresponding SignatureScheme
            
        Raises:
            ValueError: If the flag is not recognized
        """
        if flag == 0x00:
            return cls.ED25519
        elif flag == 0x01:
            return cls.SECP256K1
        elif flag == 0x02:
            return cls.SECP256R1
        else:
            raise ValueError(f"Unknown signature scheme flag: {flag:#x}") 