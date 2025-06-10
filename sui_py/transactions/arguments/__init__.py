"""
Transaction argument types for Programmable Transaction Blocks.

This module defines all argument types used in Sui transactions:
- PTB Input Arguments: Pure values and object references that go in PTB inputs vector
- Transaction Arguments: References used within commands (GasCoin, Input, Result, NestedResult)

All arguments implement the BCS protocol for proper serialization.
"""

from ...bcs import BcsSerializable, Serializer, Deserializer

from .types import (
    TransactionArgumentKind,
    PTBInputArgument,
    TransactionArgument,
    AnyArgument,
)
from .pure import PureArgument, pure
from .object import ObjectArgument, UnresolvedObjectArgument, ReceivingArgument, object_arg, receiving_arg
from .gas import GasCoinArgument, gas_coin
from .input import InputArgument
from .result import (
    ResultArgument,
    NestedResultArgument,
    result,
    nested_result,
)


def deserialize_ptb_input(deserializer: Deserializer) -> PTBInputArgument:
    """
    Deserialize a PTB input argument (CallArg in C# SDK).
    
    PTB Input tag values:
    - Pure = 0
    - Object = 1
    
    Note: UnresolvedObjectArgument should not appear in serialized data
    as objects must be resolved before serialization.
    
    Args:
        deserializer: The BCS deserializer
        
    Returns:
        The deserialized PTB input argument
        
    Raises:
        ValueError: If the argument tag is unknown
    """
    tag = deserializer.read_u8()
    if tag == 0:  # Pure
        return PureArgument.deserialize(deserializer)
    elif tag == 1:  # Object
        # Check object ref type to determine if it's regular or receiving
        obj_ref_type = deserializer.read_u8()  # ObjectRefType
        if obj_ref_type == 0:  # ImmOrOwned
            return ObjectArgument.deserialize(deserializer)
        elif obj_ref_type == 2:  # Receiving
            return ReceivingArgument.deserialize(deserializer)
        else:
            raise ValueError(f"Unknown object ref type: {obj_ref_type}")
    else:
        raise ValueError(f"Unknown PTB input argument tag: {tag}")


def deserialize_transaction_argument(deserializer: Deserializer) -> TransactionArgument:
    """
    Deserialize a transaction argument.
    
    Transaction Argument tag values:
    - GasCoin = 0
    - Input = 1
    - Result = 2
    - NestedResult = 3
    
    Args:
        deserializer: The BCS deserializer
        
    Returns:
        The deserialized transaction argument
        
    Raises:
        ValueError: If the argument tag is unknown
    """
    tag = deserializer.read_u8()
    if tag == TransactionArgumentKind.GasCoin:
        return GasCoinArgument.deserialize(deserializer)
    elif tag == TransactionArgumentKind.Input:
        return InputArgument.deserialize(deserializer)
    elif tag == TransactionArgumentKind.Result:
        return ResultArgument.deserialize(deserializer)
    elif tag == TransactionArgumentKind.NestedResult:
        return NestedResultArgument.deserialize(deserializer)
    else:
        raise ValueError(f"Unknown transaction argument tag: {tag}")


__all__ = [
    # Types
    "TransactionArgumentKind",
    "PTBInputArgument",
    "TransactionArgument",
    "AnyArgument",
    
    # Classes
    "PureArgument",
    "ObjectArgument",
    "UnresolvedObjectArgument",
    "ReceivingArgument",
    "GasCoinArgument",
    "InputArgument",
    "ResultArgument",
    "NestedResultArgument",
    
    # Factory functions
    "pure",
    "object_arg",
    "receiving_arg",
    "gas_coin",
    "result",
    "nested_result",
    
    # Deserialization
    "deserialize_ptb_input",
    "deserialize_transaction_argument",
]
