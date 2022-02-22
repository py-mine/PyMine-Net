from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.chat import Chat
from pymine_net.types.packet import ClientBoundPacket

__all__ = ("PlayPlayerListHeaderAndFooter",)


class PlayPlayerListHeaderAndFooter(ClientBoundPacket):
    """Sent to display additional information above/below the client's player list.

    :param Chat header: Content to display above player list.
    :param Chat footer: Content to display below player list.
    :ivar int id: Unique packet ID.
    :ivar header:
    :ivar footer:
    """

    id = 0x5F

    def __init__(self, header: Chat, footer: Chat):
        super().__init__()

        self.header = header
        self.footer = footer

    def pack(self) -> Buffer:
        return Buffer().write_chat(self.header).write_chat(self.footer)
