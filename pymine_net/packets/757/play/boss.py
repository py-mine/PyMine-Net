"""Contains packets related to bosses."""

from __future__ import annotations

import uuid

from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.buffer import Buffer
from pymine_net.types.chat import Chat

__all__ = ("PlayBossBar",)


#90% sure this is good but probably should be checked by someone else
class PlayBossBar(ClientBoundPacket):
    """Used to send boss bar data. (Server -> Client)

    :param uuid.UUID uuid: UUID of the boss bar.
    :param int action: Action to take.
    :param type **data: Data corresponding to the action.
    :ivar type data: Data corresponding to the action.
    :ivar int id: Unique packet ID.
    :ivar uuid:
    :ivar action:
    """

    id = 0x0D

    def __init__(self, uuid: uuid.UUID, action: int, **data: dict):
        super().__init__()

        self.uuid = uuid
        self.action = action
        self.data = data

    def pack(self) -> Buffer:
        buf = Buffer.write_uuid(self.uuid).write_varint(self.action)

        if self.action == 0:
            buf += (
                buf.write_chat(
                self.data["title"]).write(
                "f", self.data["health"]).write_varint(
                self.data["color"]).write_varint(
                self.data["division"]).write(
                "B", self.data["flags"])
            )
        elif self.action == 2:
            buf += buf.write("f", self.data["health"])
        elif self.action == 3:
            buf += buf.write_chat(self.data["title"])
        elif self.action == 4:
            buf += buf.write_varint(self.data["color"]).write_varint(
                self.data["division"]
            )
        elif self.action == 5:
            buf += buf.write("B", self.data["flags"])

        return buf
