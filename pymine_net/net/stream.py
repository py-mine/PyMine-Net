
from re import L
from typing import Tuple
from pymine_net.strict_abc import abstract


class AbstractTCPStream:
    """Abstract class for a TCP stream."""

    @property
    def remote(self) -> Tuple[str, int]:
        raise NotImplementedError

    @abstract
    def read_varint(self) -> int:
        pass
