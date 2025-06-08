"""
Common types and enums for transaction arguments.
"""

from enum import IntEnum
from typing import Union
from ...bcs import BcsSerializable, Serializer, Deserializer

# Forward references for type hints
PureArgument = object
ObjectArgument = object
GasCoinArgument = object
InputArgument = object
ResultArgument = object
NestedResultArgument = object
UnresolvedObjectArgument = object


class TransactionArgumentKind(IntEnum):
    """
    Enum representation of TransactionArgument types.
    
    These values correspond to the BCS enum variant tags used in serialization,
    and match the C# SDK TransactionArgumentKind enum exactly.
    """
    GasCoin = 0
    Input = 1
    Result = 2 
    NestedResult = 3


# Type for PTB input arguments (what goes in the PTB inputs vector)
PTBInputArgument = Union[
    "PureArgument",
    "ObjectArgument",
    "UnresolvedObjectArgument",
]

# Type for transaction arguments used in commands
TransactionArgument = Union["GasCoinArgument", "InputArgument", "ResultArgument", "NestedResultArgument"]

# Type alias for all argument types
AnyArgument = Union[PTBInputArgument, TransactionArgument]
