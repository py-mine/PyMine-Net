"""Contains packets related to advancements."""

from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = (
    "PlayAdvancementTab",
    "PlaySelectAdvancementTab"
)


class PlayAdvancementTab(ServerBoundPacket):
    """Related to advancement tab menu, see here: https://wiki.vg/Protocol#Advancement_Tab (Client -> Server)

    :param int action: Either opened tab (0), or closed screen (1).
    :param int tab_id: The ID of the tab, only present if action is 0 (opened tab).
    :ivar int id: Unique packet ID.
    :ivar action:
    :ivar tab_id:
    """

    id = 0x22

    def __init__(self, action: int, tab_id: int):
        super().__init__()

        self.action = action
        self.tab_id = tab_id

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayAdvancementTab:
        return cls(buf.read_varint(), buf.read_optional(buf.read_varint))


class PlaySelectAdvancementTab(ClientBoundPacket):
    """Sent by the server to indicate that the client should switch advancement tab. Sent either when the client switches tab in the GUI or when an advancement in another tab is made. (Server -> Client)

    :param Optional[str] identifier: One of the following: minecraft:story/root, minecraft:nether/root, minecraft:end/root, minecraft:adventure/root, minecraft:husbandry/root.
    :ivar int id: Unique packet ID.
    :ivar Optional[str] identifier:
    """

    id = 0x40

    def __init__(self, identifier: str = None):
        super().__init__()

        self.identifier = identifier

    def pack(self) -> Buffer:
        buf = Buffer()
        return buf.write_optional(buf.write_string, self.identifier)
