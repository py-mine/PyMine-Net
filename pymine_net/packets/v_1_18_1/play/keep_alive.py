"""Contains packets for maintaining the connection between client and server."""

from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = ("PlayKeepAliveClientBound", "PlayKeepAliveServerBound")


class PlayKeepAliveClientBound(ClientBoundPacket):
    """Sent by the server in order to maintain connection with the client. (Server -> Client)

    :param int keep_alive_id: A randomly generated (by the server) integer/long.
    :ivar int id: Unique packet ID.
    :ivar keep_alive_id:
    """

    id = 0x21

    def __init__(self, keep_alive_id: int):
        super().__init__()

        self.keep_alive_id = keep_alive_id

    def pack(self) -> Buffer:
        return Buffer().write("q", self.keep_alive_id)


class PlayKeepAliveServerBound(ServerBoundPacket):
    """Sent by client in order to maintain connection with server. (Client -> Server)

    :param int keep_alive_id: A randomly generated (by the server) integer/long.
    :ivar int id: Unique packet ID.
    :ivar keep_alive_id:
    """

    id = 0x0F

    def __init__(self, keep_alive_id: int):
        super().__init__()

        self.keep_alive_id = keep_alive_id

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayKeepAliveServerBound:
        return cls(buf.read("q"))
