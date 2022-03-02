from abc import abstractmethod


class AbstractTCPStream:
    """Abstract class for a TCP stream."""

    @abstractmethod
    def read_varint(self) -> int:
        pass
