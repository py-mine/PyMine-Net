from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = ("StatusStatusRequest", "StatusStatusResponse", "StatusStatusPingPong")


class StatusStatusRequest(ServerBoundPacket):
    """Request from the client to get information on the server. (Client -> Server)

    :ivar int id: Unique packet ID.
    """

    id = 0x00

    def __init__(self):
        super().__init__()

    def pack(self) -> Buffer:
        return Buffer()

    @classmethod
    def unpack(cls, buf: Buffer) -> StatusStatusRequest:
        return cls()


class StatusStatusResponse(ClientBoundPacket):
    """Returns server status data back to the requesting client. (Server -> Client)

    :param dict data: JSON response data sent back to the client.
    :ivar int id: Unique packet ID.
    :ivar data:
    """

    id = 0x00

    def __init__(self, data: dict):
        super().__init__()

        self.data = data

    def pack(self) -> Buffer:
        return Buffer().write_json(self.data)
        
    @classmethod
    def unpack(cls, buf: Buffer) -> StatusStatusResponse:
        return cls(buf.read_json())


class StatusStatusPingPong(ServerBoundPacket, ClientBoundPacket):
    """Ping pong? (Client <-> Server)

    :param int payload: A long number, randomly generated or what the client sent.
    :ivar int id: Unique packet ID.
    :ivar int payload:
    """

    id = 0x01

    def __init__(self, payload: int):
        super().__init__()

        self.payload = payload

    @classmethod
    def unpack(cls, buf: Buffer) -> StatusStatusPingPong:
        return cls(buf.read("q"))

    def pack(self) -> Buffer:
        return Buffer().write("q", self.payload)
