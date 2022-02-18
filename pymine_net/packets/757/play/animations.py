"""Contains animation packets."""

from __future__ import annotations

from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.buffer import Buffer

__all__ = (
    "PlayEntityAnimation",
    "PlayBlockBreakAnimation",
    "PlayAnimationServerBound",
    "PlayOpenBook",
)


class PlayEntityAnimation(ClientBoundPacket):
    """Sent whenever an entity should change animation. (Server -> Client)

    :param int entity_id: Entity ID of the digging entity.
    :param int animation: Value 0-5 which correspond to a specific animation (https://wiki.vg/Protocol#Entity_Animation_.28clientbound.29).
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar animation:
    """

    id = 0x06

    def __init__(self, entity_id: int, animation: int):
        super().__init__()

        self.entity_id = entity_id
        self.animation = animation

    def pack(self) -> Buffer:
        return Buffer().write_varint(self.entity_id).write("B", self.animation)
