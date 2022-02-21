"""Contains the PlaySetCooldown packet."""

from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket

__all__ = ("PlaySetCooldown",)


class PlaySetCooldown(ClientBoundPacket):
    """Applies a cooldown period to all items with the given type. (Server -> Client)

    Client bound(Server -> Client)
    :param int item_id: The unique id of the type of affected items.
    :param int cooldown_ticks: The length of the cooldown in in-game ticks.
    :ivar int id: The unique ID of the packet.
    :ivar item_id:
    :ivar cooldown_ticks:
    """

    id = 0x17

    def __init__(self, item_id: int, cooldown_ticks: int) -> None:
        super().__init__()

        self.item_id = item_id
        self.cooldown_ticks = cooldown_ticks

    def pack(self) -> Buffer:
        return Buffer().write_varint(self.item_id).write_varint(self.cooldown_ticks)
