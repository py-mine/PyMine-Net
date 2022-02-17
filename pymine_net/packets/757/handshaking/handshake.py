from __future__ import annotations

from pymine_net.enums import PacketDirection
from pymine_net import ClientPacket, Buffer


class HandshakeHandshake(ClientPacket):
    """Initiates the connection between the server and client. (Client -> Server)

    :param int protocol: Protocol version to be used.
    :param str address: The host/address the client is connecting to.
    :param int port: The port the client is connection on.
    :param int next_state: The next state which the server should transfer to. 1 for status, 2 for login.
    :ivar int id: Unique packet ID.
    :ivar protocol:
    :ivar address:
    :ivar port:
    :ivar next_state:
    """

    id = 0x00

    def __init__(self, protocol: int, address: str, port: int, next_state: int):
        super().__init__()

        self.protocol = protocol
        self.address = address
        self.port = port
        self.next_state = next_state

    @classmethod
    def unpack(cls, buf: Buffer) -> HandshakeHandshake:
        return cls(
            buf.read_varint(), buf.read_string(), buf.read("H"), buf.read_varint()
        )
