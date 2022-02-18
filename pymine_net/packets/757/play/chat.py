"""Contains packets related to the chat."""

from __future__ import annotations

import uuid

from pymine_net.types.packet import ClientBoundPacket
from pymine_net.types.buffer import Buffer
from pymine_net.types.chat import Chat

__all__ = (
    "PlayChatMessageClientBound",
    "PlayChatMessageServerBound",
    "PlayTabCompleteClientBound",
    "PlayTabCompleteServerBound",
    "PlayTitle",
)


class PlayChatMessageClientBound(ClientBoundPacket):
    """A chat message from the server to the client (Server -> Client)

    :param Chat data: The actual chat data.
    :param int position: Where on the GUI the message is to be displayed.
    :param uuid.UUID sender: Unknown, see here: https://wiki.vg/Protocol#Chat_Message_.28clientbound.29.
    :ivar int id: Unique packet ID.
    :ivar data:
    :ivar position:
    :ivar sender:
    """

    id = 0x0F

    def __init__(self, data: Chat, position: int, sender: uuid.UUID):
        super().__init__()

        self.data = data
        self.position = position
        self.sender = sender

    def pack(self) -> Buffer:
        return Buffer().write_chat(self.data).write("b", self.position).write_uuid(self.sender)
