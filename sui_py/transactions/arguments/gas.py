"""
Gas coin argument implementation.
"""

from dataclasses import dataclass
from typing_extensions import Self

from ...bcs import BcsSerializable, Serializer, Deserializer
from .types import TransactionArgumentKind

from ...utils.logging import setup_logging, get_logger
import logging

setup_logging(level=logging.DEBUG, use_emojis=True)
logger = get_logger("sui_py.transactions.arguments.gas.GasCoinArgument")

@dataclass(frozen=True)
class GasCoinArgument(BcsSerializable):
    """
    Special reference to the gas coin.
    
    This argument type represents the gas coin being used to pay for
    the transaction, which can be used in commands like coin splitting.
    """
    
    def serialize(self, serializer: Serializer) -> None:
        """Serialize with TransactionArgument enum format."""
        serializer.write_u8(TransactionArgumentKind.GasCoin)
        # Gas coin has no additional data
        logger.debug(f"Serialized gas coin argument: {list(serializer.to_bytes())}")
    
    @classmethod
    def deserialize(cls, deserializer: Deserializer) -> Self:
        """Deserialize a gas coin argument."""
        return cls()


def gas_coin() -> GasCoinArgument:
    """Create a gas coin argument."""
    return GasCoinArgument()
