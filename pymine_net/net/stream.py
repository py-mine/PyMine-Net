from pymine_net.strict_abc import abstract


class AbstractTCPStream:
    """Abstract class for a TCP stream."""

    @abstract
    def read_varint(self) -> int:
        pass
