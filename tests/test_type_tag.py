#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '.')

from sui_py.types.type_tag import parse_type_tag, StructTypeTag
from sui_py.bcs import serialize

# Test the specific type from our failing test
type_str = "0x0000000000000000000000000000000000000000000000000000000000000002::capy::Capy"

print(f"Parsing type string: {type_str}")
type_tag = parse_type_tag(type_str)
print(f"Parsed TypeTag: {type_tag}")
print(f"TypeTag type: {type(type_tag)}")

if isinstance(type_tag, StructTypeTag):
    print(f"Address: {type_tag.address}")
    print(f"Module: {type_tag.module}")
    print(f"Name: {type_tag.name}")
    print(f"Type params: {type_tag.type_params}")

# Test serialization
serialized = serialize(type_tag)
print(f"Serialized length: {len(serialized)} bytes")
print(f"Serialized hex: {serialized.hex()}")

# Compare with expected pattern from debug
expected_pattern = "07000000000000000000000000000000000000000000000000000000000000000204636170790443617079000"
print(f"Expected pattern: {expected_pattern}")
print(f"Matches expected: {serialized.hex().startswith(expected_pattern[:-1])}")  # Remove last '0' in case 