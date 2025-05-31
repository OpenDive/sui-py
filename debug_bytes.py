#!/usr/bin/env python3

actual = bytes.fromhex('0000010100100000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000207646973706c6179036e657701070000000000000000000000000000000000000000000000000000000000000002046361707904436170790001010010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000bad0110000000000000000000000000000000000000000000000000000000000000001027000000000000140001020304050607080900010203040506070809000000000000000000000000000000000000000000000000000000000000000002010000000000000040420f000000000000')
expected = bytes.fromhex('0000010100100000000000000000000000000000000000000000000000000000000000000010270000000000001400010203040506070809000102030405060708090100000000000000000000000000000000000000000000000000000000000000000207646973706c6179036e657701070000000000000000000000000000000000000000000000000000000000000002046361707904436170790001010000000000000000000000000000000000000000000000000000000000000000000bad0110000000000000000000000000000000000000000000000000000000000000001027000000000000140001020304050607080900010203040506070809000000000000000000000000000000000000000000000000000000000000000002010000000000000040420f000000000000')

print('GREAT PROGRESS! TransactionBuilder fixed the major duplication issue')
print(f'Now failing at index 37 instead of 160')
print(f'Actual length: {len(actual)} bytes')
print(f'Expected length: {len(expected)} bytes') 
print(f'Difference: {len(actual) - len(expected)} bytes')
print()

print('Analyzing failure at index 37:')
print(f'Actual   [35-45]: {actual[35:45].hex()}')
print(f'Expected [35-45]: {expected[35:45].hex()}')
print()

print('Looking at PTB inputs section:')
# PTB should start at byte 1 
# Find first difference
for i in range(min(len(actual), len(expected))):
    if actual[i] != expected[i]:
        print(f'First difference at index {i}:')
        print(f'  Actual: {actual[i]:02x}')
        print(f'  Expected: {expected[i]:02x}')
        break

print()
print('PTB structure analysis:')
print('Expected PTB starts with: 01 00 10 00 00... (1 input, then ObjectRef)')
print('Our PTB starts with:      01 00 10 00 00... (1 input)')
print()

# Look for the ObjectRef pattern in both
obj_pattern = "1000000000000000000000000000000000000000000000000000000000000000"
version_pattern = "1027000000000000"

obj_pos_actual = actual.hex().find(obj_pattern) // 2
obj_pos_expected = expected.hex().find(obj_pattern) // 2

print(f'ObjectID pattern found:')
print(f'  In actual at byte: {obj_pos_actual}')  
print(f'  In expected at byte: {obj_pos_expected}')
print(f'  Offset difference: {obj_pos_actual - obj_pos_expected} bytes')

print()
print('The issue might be in the ObjectRef serialization or ObjectArgument structure')
print('Let me check the exact input encoding...')

# PTB structure should be:
# - Vector length of inputs (1)
# - Input #0: ObjectArgument 
# - Vector length of commands (1)  
# - Command #0: MoveCall

print()
print('Expected input section (starting at byte 1):')
print(f'Byte 1: {expected[1]:02x} = {expected[1]} (should be 1 for 1 input)')
print(f'Byte 2: {expected[2]:02x} = {expected[2]} (argument type - 1=Object)')

print()
print('Our input section:')  
print(f'Byte 1: {actual[1]:02x} = {actual[1]} (inputs count)')
print(f'Byte 2: {actual[2]:02x} = {actual[2]} (argument type)')

print()
if len(actual) > 37 and len(expected) > 37:
    print('Bytes around the failure point:')
    print(f'Expected [30-50]: {expected[30:50].hex()}')
    print(f'Actual   [30-50]: {actual[30:50].hex()}') 