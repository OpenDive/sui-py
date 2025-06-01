#!/usr/bin/env python3
"""Debug vector serialization of arguments."""

from sui_py.transactions.arguments import PureArgument, ObjectArgument
from sui_py.types import ObjectRef
from sui_py.bcs import Serializer, Deserializer, BcsVector

def debug_vector_serialization():
    """Debug serialization of a vector of PTB input arguments."""
    print("=== Debugging Vector Serialization ===")
    
    # Create the same arguments as in our failing test
    obj_ref = ObjectRef(
        object_id="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        version=1,
        digest="round_trip_digest"
    )
    obj_arg = ObjectArgument(object_ref=obj_ref)
    pure_arg1 = PureArgument(bcs_bytes=b'\xe8\x03\x00\x00\x00\x00\x00\x00')  # 1000 as u64
    pure_arg2 = PureArgument(bcs_bytes=b'D0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab')
    
    print(f"Creating vector with:")
    print(f"  [0] {type(obj_arg).__name__} (tag {obj_arg.get_argument_tag()})")
    print(f"  [1] {type(pure_arg1).__name__} (tag {pure_arg1.get_argument_tag()})")
    print(f"  [2] {type(pure_arg2).__name__} (tag {pure_arg2.get_argument_tag()})")
    
    # Create vector
    args_vector = BcsVector([obj_arg, pure_arg1, pure_arg2])
    
    # Serialize the vector
    serializer = Serializer()
    args_vector.serialize(serializer)
    vector_bytes = serializer.to_bytes()
    
    print(f"\nVector serialized to {len(vector_bytes)} bytes")
    print(f"First 20 bytes: {vector_bytes[:20].hex()}")
    
    # Manual byte inspection
    print(f"\nManual inspection:")
    print(f"Byte 0 (vector length): {vector_bytes[0]} (0x{vector_bytes[0]:02x})")
    if len(vector_bytes) > 1:
        print(f"Byte 1 (first element tag): {vector_bytes[1]} (0x{vector_bytes[1]:02x})")
    
    # Try to deserialize the vector
    print(f"\nAttempting vector deserialization...")
    try:
        from sui_py.transactions.arguments import deserialize_ptb_input
        deserializer = Deserializer(vector_bytes)
        restored_vector = BcsVector.deserialize(deserializer, deserialize_ptb_input)
        
        print(f"✅ Vector deserialized successfully!")
        print(f"Restored {len(restored_vector.elements)} elements:")
        for i, elem in enumerate(restored_vector.elements):
            print(f"  [{i}] {type(elem).__name__} (tag {elem.get_argument_tag()})")
            
    except Exception as e:
        print(f"❌ Vector deserialization failed: {e}")
        
        # Manual element by element
        print(f"\nManual element-by-element parsing:")
        try:
            deserializer = Deserializer(vector_bytes)
            vector_length = deserializer.read_vector_length()
            print(f"Vector length: {vector_length}")
            
            for i in range(min(vector_length, 5)):
                print(f"\nElement {i}:")
                try:
                    # Read the tag byte
                    tag = deserializer.read_u8()
                    print(f"  Tag: {tag} (0x{tag:02x})")
                    
                    if tag == 17:
                        print(f"  ❌ Found problematic tag 17!")
                        
                        # Look at surrounding bytes
                        current_pos = deserializer.offset - 1  # Back up to tag byte
                        surrounding = vector_bytes[max(0, current_pos-3):current_pos+5]
                        print(f"  Surrounding bytes: {surrounding.hex()}")
                        break
                    elif tag == 0:
                        # PureArgument - read the data
                        data_length = deserializer.read_vector_length()
                        data = deserializer.read_bytes(data_length)
                        print(f"  Pure data length: {data_length}")
                        print(f"  Pure data: {data.hex()}")
                    elif tag == 1:
                        # ObjectArgument - read object ref
                        obj_id = deserializer.read_bytes(32)
                        version = deserializer.read_u64()
                        digest_len = deserializer.read_vector_length()
                        digest = deserializer.read_bytes(digest_len)
                        print(f"  Object ID: {obj_id.hex()}")
                        print(f"  Version: {version}")
                        print(f"  Digest: {digest}")
                    else:
                        print(f"  Unknown tag: {tag}")
                        break
                        
                except Exception as e2:
                    print(f"  Error parsing element {i}: {e2}")
                    break
                    
        except Exception as e2:
            print(f"Failed to read vector length: {e2}")

if __name__ == "__main__":
    debug_vector_serialization() 