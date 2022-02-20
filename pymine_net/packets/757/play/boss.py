"""Contains packets related to bosses."""

from __future__ import annotations

from uuid import UUID

from pymine_net.types.buffer import Buffer
from pymine_net.types.chat import Chat
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = ("PlayBossBar",)


class PlayBossBar(ClientBoundPacket):
    """Used to send boss bar data. (Server -> Client)

    :param UUID uuid: UUID of the boss bar.
    :param int action: Action to take.
    :param dict **data: Data corresponding to the action.
    :ivar dict data: Data corresponding to the action.
    :ivar int id: Unique packet ID.
    :ivar uuid:
    :ivar action:
    """

    id = 0x0D

    def __init__(self, uuid: UUID, action: int, **data: dict):
        super().__init__()

        self.uuid = uuid
        self.action = action
        self.data = data

    def pack(self) -> Buffer:
        buf = Buffer.write_uuid(self.uuid).write_varint(self.action)

        if self.action == 0:
            buf.write_chat(self.data["title"]).write("f", self.data["health"]).write_varint(
                self.data["color"]
            ).write_varint(self.data["division"]).write("B", self.data["flags"])
        elif self.action == 2:
            buf.write("f", self.data["health"])
        elif self.action == 3:
            buf.write_chat(self.data["title"])
        elif self.action == 4:
            buf.write_varint(self.data["color"]).write_varint(self.data["division"])
        elif self.action == 5:
            buf.write("B", self.data["flags"])

        return buf
