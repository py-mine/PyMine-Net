from __future__ import annotations

from pymine_net.enums import PacketDirection
from pymine_net import ClientPacket, ServerPacket, Buffer


# see https://wiki.vg/Server_List_Ping for more information


class StatusStatusRequest(ClientPacket):
    """Request from the client to get information on the server. (Client -> Server)

    :ivar int id: Unique packet ID.
    """

    id = 0x00
    to = PacketDirection.TO_SERVER

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def unpack(cls, buf: Buffer) -> StatusStatusRequest:
        return cls()


class StatusStatusResponse(ServerPacket):
    """Returns server status data back to the requesting client. (Server -> Client)

    :param dict response_data: JSON response data sent back to the client.
    :ivar int id: Unique packet ID.
    :ivar response_data:
    """

    id = 0x00

    def __init__(self, response_data: dict) -> None:
        super().__init__()

        self.response_data = response_data

    def pack(self) -> Buffer:
        return Buffer().write_json(self.response_data)
