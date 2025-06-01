#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '.')

from sui_py import TransactionBuilder
from sui_py.bcs import serialize
from sui_py.types import ObjectRef
from sui_py.transactions.arguments import ObjectArgument
from sui_py.transactions.commands import MoveCallCommand
from sui_py.transactions.ptb import ProgrammableTransactionBlock

# Test data from the failing test
object_id = "0x1000000000000000000000000000000000000000000000000000000000000000"
version = 10000
digest = "1Bhh3pU9gLXZhoVxkr5wyg9sX6"
sui_address_hex = "0x0000000000000000000000000000000000000000000000000000000000000002"

print("=== UNDERSTANDING THE STRUCTURE ===")

# What the C# test expects:
# - PTB should have 1 input (ObjectArgument with the payment object)
# - PTB should have 1 command (MoveCall)
# - The MoveCall arguments should reference the input by INDEX, not embed the object

print("\n1. Create the ObjectArgument for the PTB input:")
payment_ref = ObjectRef(
    object_id=object_id,
    version=version,
    digest=digest
)
object_input = ObjectArgument(payment_ref)
print(f"Object input: {object_input}")
print(f"Object input serialized: {serialize(object_input).hex()}")

print("\n2. What should the MoveCall command arguments be?")
print("According to TypeScript, commands should use { Input: index } references, not full objects")

# In TypeScript, this would be something like:
# { $kind: 'Input', Input: 0 }
# which serializes as just the input index

# The issue is that our TransactionBuilder is passing the full ObjectArgument
# to the command, when it should pass some kind of index reference

print("\n3. Let's see what TransactionBuilder creates:")
tx = TransactionBuilder()
payment_obj = tx.object(object_id, version, digest)
print(f"TransactionBuilder created: {payment_obj}")
print(f"Type: {type(payment_obj)}")

move_result = tx.move_call(
    target=f"{sui_address_hex}::display::new",
    arguments=[payment_obj],
    type_arguments=[f"{sui_address_hex}::capy::Capy"]
)

ptb = tx.build()
print(f"\nPTB inputs: {len(ptb.inputs)}")
print(f"PTB commands: {len(ptb.commands)}")

cmd = ptb.commands[0]
print(f"\nCommand arguments: {cmd.arguments}")
print(f"Command argument type: {type(cmd.arguments[0])}")

print("\n4. The problem:")
print("- PTB inputs should contain the ObjectArgument")  
print("- Command arguments should contain index references (0, 1, 2, etc.)")
print("- But our commands are getting the full ObjectArgument objects")

print("\n5. Possible solutions:")
print("A. TransactionBuilder should return index references, not the full objects")
print("B. Commands should convert full objects to index references when building")
print("C. We need a new InputReference argument type")

print("\n6. Let's check the inputs vs arguments:")
print(f"PTB input 0: {ptb.inputs[0]}")
print(f"Command arg 0: {cmd.arguments[0]}")
print(f"Are they the same object? {ptb.inputs[0] is cmd.arguments[0]}")

print("\n7. What TypeScript does:")
print("- tx.object() returns { $kind: 'Input', Input: index }")
print("- This gets passed to commands as arguments")  
print("- The actual object data is only in ptb.inputs[index]")
print("- Commands serialize their arguments as references to inputs") 