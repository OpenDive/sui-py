#!/usr/bin/env python3
"""Debug script to investigate PTB input serialization issues."""

import sys
import os
sys.path.insert(0, '.')

from sui_py import TransactionBuilder
from sui_py.bcs import serialize
from sui_py.types import ObjectRef
from sui_py.transactions import ProgrammableTransactionBlock
from sui_py.bcs import Deserializer

# Test data from the failing test
object_id = "0x1000000000000000000000000000000000000000000000000000000000000000"
version = 10000
digest = "1Bhh3pU9gLXZhoVxkr5wyg9sX6"
sui_address_hex = "0x0000000000000000000000000000000000000000000000000000000000000002"

print("=== PTB DEBUG ANALYSIS ===")

def debug_serialization_roundtrip():
    """Debug the exact serialization roundtrip that's failing."""
    print("=== Debugging Serialization Round Trip ===")
    
    tx = TransactionBuilder()
    
    # Replicate the exact example that's failing
    coin = tx.object(
        "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        version=1,
        digest="round_trip_digest"
    )
    amount = tx.pure(1000, "u64")
    recipient = tx.pure("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab")
    
    new_coins = tx.split_coins(coin, [amount])
    tx.transfer_objects([new_coins[0]], recipient)
    
    print(f"Built transaction with:")
    print(f"  PTB Inputs: {len(tx._inputs)}")
    for i, inp in enumerate(tx._inputs):
        print(f"    {i}: {type(inp).__name__} (tag {inp.get_argument_tag()})")
    
    # Build PTB
    ptb = tx.build()
    print(f"  PTB Commands: {len(ptb.commands)}")
    
    # Serialize
    original_bytes = ptb.to_bytes()
    print(f"  Serialized to {len(original_bytes)} bytes")
    
    # Try to deserialize
    print(f"\nAttempting deserialization...")
    try:
        deserializer = Deserializer(original_bytes)
        restored_ptb = ProgrammableTransactionBlock.deserialize(deserializer)
        print(f"✅ Deserialization successful!")
        print(f"  Restored inputs: {len(restored_ptb.inputs)}")
        print(f"  Restored commands: {len(restored_ptb.commands)}")
        
    except Exception as e:
        print(f"❌ Deserialization failed: {e}")
        
        # Let's manually inspect the bytes
        print(f"\nManual byte inspection:")
        print(f"First 20 bytes: {original_bytes[:20].hex()}")
        
        # Try to deserialize just the inputs vector
        try:
            from sui_py.bcs import BcsVector
            from sui_py.transactions.arguments import deserialize_ptb_input
            
            deserializer = Deserializer(original_bytes)
            print(f"Reading inputs vector...")
            inputs_vector = BcsVector.deserialize(deserializer, deserialize_ptb_input)
            print(f"✅ Inputs deserialized successfully: {len(inputs_vector.elements)} inputs")
            
        except Exception as e2:
            print(f"❌ Inputs deserialization failed: {e2}")
            
            # Let's see what the individual bytes are
            deserializer = Deserializer(original_bytes)
            try:
                input_count = deserializer.read_vector_length()
                print(f"Input vector length: {input_count}")
                
                for i in range(min(input_count, 5)):  # Only try first 5
                    try:
                        tag = deserializer.read_u8()
                        print(f"  Input {i} tag: {tag} (0x{tag:02x})")
                        if tag == 17:
                            print(f"    ❌ Found problematic tag 17!")
                            break
                        elif tag == 0:
                            # Pure argument - read length and data
                            length = deserializer.read_vector_length() 
                            data = deserializer.read_bytes(length)
                            print(f"    Pure arg: {length} bytes = {data.hex()}")
                        elif tag == 1:
                            # Object argument - try to read it
                            print(f"    Object arg detected")
                            # Skip the object data for now
                            break
                        else:
                            print(f"    Unknown tag: {tag}")
                            break
                    except Exception as e3:
                        print(f"    Error reading input {i}: {e3}")
                        break
                        
            except Exception as e3:
                print(f"Failed to read input vector length: {e3}")

def debug_ptb_inputs():
    """Debug what's actually in PTB inputs."""
    print("=== Debugging PTB Inputs ===")
    
    tx = TransactionBuilder()
    
    # Create some inputs
    coin = tx.object('0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef', version=1, digest='test')
    amount = tx.pure(1000, 'u64')
    recipient = tx.pure('0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab')
    
    print(f"PTB Inputs ({len(tx._inputs)}):")
    for i, inp in enumerate(tx._inputs):
        print(f"  {i}: {type(inp).__name__} - {inp}")
        print(f"      Tag: {inp.get_argument_tag()}")
    
    print(f"\nCommand arguments returned:")
    print(f"  coin: {type(coin).__name__} - {coin}")
    print(f"  amount: {type(amount).__name__} - {amount}")  
    print(f"  recipient: {type(recipient).__name__} - {recipient}")
    
    # Try building the PTB
    try:
        ptb = tx.build()
        print(f"\nPTB built successfully:")
        print(f"  Inputs: {len(ptb.inputs)}")
        print(f"  Commands: {len(ptb.commands)}")
        
        # Check what's actually in PTB inputs
        print(f"\nActual PTB inputs:")
        for i, inp in enumerate(ptb.inputs):
            print(f"  {i}: {type(inp).__name__} - tag={inp.get_argument_tag()}")
            
    except Exception as e:
        print(f"\nError building PTB: {e}")

if __name__ == "__main__":
    debug_ptb_inputs()
    print("\n" + "="*60 + "\n")
    debug_serialization_roundtrip()

# Build the PTB using TransactionBuilder
tx = TransactionBuilder()
payment_obj = tx.object(object_id)

move_result = tx.move_call(
    target=f"{sui_address_hex}::display::new",
    arguments=[payment_obj],
    type_arguments=[f"{sui_address_hex}::capy::Capy"]
)

ptb = tx.build()

print(f"TransactionBuilder inputs: {len(tx._inputs)}")
print(f"PTB inputs: {len(ptb.inputs)}")
print(f"PTB commands: {len(ptb.commands)}")
print()

print("Input details:")
for i, inp in enumerate(ptb.inputs):
    print(f"  Input {i}: {type(inp).__name__} = {inp}")
    if hasattr(inp, 'object_ref'):
        print(f"    Object ref: {inp.object_ref}")
        
print()
print("Command details:")
for i, cmd in enumerate(ptb.commands):
    print(f"  Command {i}: {type(cmd).__name__}")
    if hasattr(cmd, 'arguments'):
        print(f"    Arguments: {[type(arg).__name__ for arg in cmd.arguments]}")
        for j, arg in enumerate(cmd.arguments):
            print(f"      Arg {j}: {arg}")

print()
print("PTB serialization:")
ptb_bytes = ptb.to_bytes()
print(f"PTB length: {len(ptb_bytes)} bytes")
print(f"PTB hex: {ptb_bytes.hex()}")

print()
print("Manual input creation (for comparison):")
payment_ref = ObjectRef(
    object_id=object_id,
    version=version,
    digest=digest
)

from sui_py.transactions.arguments import ObjectArgument
manual_obj_arg = ObjectArgument(payment_ref)
print(f"Manual ObjectArgument: {manual_obj_arg}")
print(f"Manual ObjectArgument serialized: {serialize(manual_obj_arg).hex()}")

print()
print("What the TransactionBuilder object() method creates:")
tb_obj_arg = tx.object(object_id)
print(f"TransactionBuilder ObjectArgument: {tb_obj_arg}")
print(f"TransactionBuilder ObjectArgument serialized: {serialize(tb_obj_arg).hex()}")

print()
print("Are they the same?")
print(f"Manual == TB: {str(manual_obj_arg) == str(tb_obj_arg)}")
print(f"Manual bytes == TB bytes: {serialize(manual_obj_arg) == serialize(tb_obj_arg)}") 