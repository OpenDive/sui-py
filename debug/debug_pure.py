#!/usr/bin/env python3
"""Debug PureArgument serialization specifically."""

from sui_py.transactions.arguments import PureArgument
from sui_py.bcs import Serializer, Deserializer

def debug_pure_argument():
    """Debug PureArgument serialization in detail."""
    print("=== Debugging PureArgument Serialization ===")
    
    # Create a simple pure argument
    pure_arg = PureArgument(bcs_bytes=b'\xe8\x03\x00\x00\x00\x00\x00\x00')  # 1000 as u64
    print(f"Original PureArgument: {pure_arg}")
    print(f"Tag method returns: {pure_arg.get_argument_tag()}")
    
    # Serialize it
    serializer = Serializer()
    pure_arg.serialize(serializer)
    serialized_bytes = serializer.to_bytes()
    
    print(f"Serialized bytes: {serialized_bytes.hex()}")
    print(f"Length: {len(serialized_bytes)}")
    print(f"First byte (tag): {serialized_bytes[0]} (0x{serialized_bytes[0]:02x})")
    
    # Try deserializing it back
    try:
        from sui_py.transactions.arguments import deserialize_ptb_input
        deserializer = Deserializer(serialized_bytes)
        restored = deserialize_ptb_input(deserializer)
        print(f"✅ Deserialized successfully: {restored}")
        print(f"Restored tag: {restored.get_argument_tag()}")
    except Exception as e:
        print(f"❌ Deserialization failed: {e}")
        
        # Manual byte analysis
        deserializer = Deserializer(serialized_bytes)
        tag = deserializer.read_u8()
        print(f"Manual tag read: {tag} (0x{tag:02x})")

def debug_object_argument():
    """Debug ObjectArgument serialization for comparison."""
    print("\n=== Debugging ObjectArgument Serialization ===")
    
    from sui_py.transactions.arguments import ObjectArgument
    from sui_py.types import ObjectRef
    
    # Create an object argument
    obj_ref = ObjectRef(
        object_id="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        version=1,
        digest="test_digest"
    )
    obj_arg = ObjectArgument(object_ref=obj_ref)
    print(f"Original ObjectArgument: {obj_arg}")
    print(f"Tag method returns: {obj_arg.get_argument_tag()}")
    
    # Serialize it
    serializer = Serializer()
    obj_arg.serialize(serializer)
    serialized_bytes = serializer.to_bytes()
    
    print(f"Serialized bytes (first 10): {serialized_bytes[:10].hex()}")
    print(f"First byte (tag): {serialized_bytes[0]} (0x{serialized_bytes[0]:02x})")
    
    # Try deserializing
    try:
        from sui_py.transactions.arguments import deserialize_ptb_input
        deserializer = Deserializer(serialized_bytes)
        restored = deserialize_ptb_input(deserializer)
        print(f"✅ Deserialized successfully: {type(restored).__name__}")
    except Exception as e:
        print(f"❌ Deserialization failed: {e}")

if __name__ == "__main__":
    debug_pure_argument()
    debug_object_argument() 