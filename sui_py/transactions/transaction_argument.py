"""
TransactionArgument definitions for command arguments.

This module implements the TransactionArgument system that matches the C# Unity SDK,
representing the different types of arguments that can be used in commands.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Union
from typing_extensions import Self

from ..bcs import BcsSerializable, Serializer, Deserializer


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


@dataclass
class GasCoinTransactionArgument(BcsSerializable):
    """
    Gas coin transaction argument.
    
    References the gas coin used in the transaction.
    """
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize - gas coin has no additional data."""
        pass
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes."""
        return cls()


@dataclass
class InputTransactionArgument(BcsSerializable):
    """
    Input transaction argument.
    
    References an input by its index in the PTB inputs array.
    """
    index: int
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the input index as u16."""
        serializer.write_u16(self.index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes."""
        index = deserializer.read_u16()
        return cls(index=index)


@dataclass
class ResultTransactionArgument(BcsSerializable):
    """
    Result transaction argument.
    
    References a result by its command index.
    """
    index: int
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize the command index as u16."""
        serializer.write_u16(self.index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes."""
        index = deserializer.read_u16()
        return cls(index=index)


@dataclass
class NestedResultTransactionArgument(BcsSerializable):
    """
    Nested result transaction argument.
    
    References a specific result within a command that returns multiple results.
    """
    command_index: int
    result_index: int
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize both indices as u16."""
        serializer.write_u16(self.command_index)
        serializer.write_u16(self.result_index)
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes."""
        command_index = deserializer.read_u16()
        result_index = deserializer.read_u16()
        return cls(command_index=command_index, result_index=result_index)


# Union type for all TransactionArgument variants
TransactionArgumentData = Union[
    GasCoinTransactionArgument,
    InputTransactionArgument, 
    ResultTransactionArgument,
    NestedResultTransactionArgument
]


@dataclass
class TransactionArgument(BcsSerializable):
    """
    Wrapper for TransactionArgument variants with proper enum serialization.
    
    This matches the C# SDK TransactionArgument structure where each variant
    is tagged with its enum value during serialization.
    """
    data: TransactionArgumentData
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize with enum tag followed by variant data."""
        if isinstance(self.data, GasCoinTransactionArgument):
            serializer.write_u8(TransactionArgumentKind.GasCoin)
            self.data.serialize(serializer)
        elif isinstance(self.data, InputTransactionArgument):
            serializer.write_u8(TransactionArgumentKind.Input)
            self.data.serialize(serializer)
        elif isinstance(self.data, ResultTransactionArgument):
            serializer.write_u8(TransactionArgumentKind.Result)
            self.data.serialize(serializer)
        elif isinstance(self.data, NestedResultTransactionArgument):
            serializer.write_u8(TransactionArgumentKind.NestedResult)
            self.data.serialize(serializer)
        else:
            raise ValueError(f"Unknown TransactionArgument type: {type(self.data)}")
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize from BCS bytes."""
        tag = deserializer.read_u8()
        
        if tag == TransactionArgumentKind.GasCoin:
            data = GasCoinTransactionArgument.deserialize(deserializer)
        elif tag == TransactionArgumentKind.Input:
            data = InputTransactionArgument.deserialize(deserializer)
        elif tag == TransactionArgumentKind.Result:
            data = ResultTransactionArgument.deserialize(deserializer)
        elif tag == TransactionArgumentKind.NestedResult:
            data = NestedResultTransactionArgument.deserialize(deserializer)
        else:
            raise ValueError(f"Unknown TransactionArgument tag: {tag}")
        
        return cls(data=data)
    
    @classmethod
    def gas_coin(cls) -> "TransactionArgument":
        """Create a GasCoin TransactionArgument."""
        return cls(data=GasCoinTransactionArgument())
    
    @classmethod
    def input(cls, index: int) -> "TransactionArgument":
        """Create an Input TransactionArgument."""
        return cls(data=InputTransactionArgument(index=index))
    
    @classmethod
    def result(cls, index: int) -> "TransactionArgument":
        """Create a Result TransactionArgument."""
        return cls(data=ResultTransactionArgument(index=index))
    
    @classmethod
    def nested_result(cls, command_index: int, result_index: int) -> "TransactionArgument":
        """Create a NestedResult TransactionArgument."""
        return cls(data=NestedResultTransactionArgument(
            command_index=command_index, 
            result_index=result_index
        ))


# Convenience function for backward compatibility
def deserialize_transaction_argument(deserializer: Deserializer) -> TransactionArgument:
    """Deserialize a TransactionArgument from BCS bytes."""
    return TransactionArgument.deserialize(deserializer) 