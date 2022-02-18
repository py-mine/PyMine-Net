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


class PlayBlockBreakAnimation(ClientBoundPacket):
    """Sent to play a block breaking animation. (Server -> Client)

    :param int entity_id: Entity ID of the entity which broke the block, or random.
    :param int x: The x coordinate of the location to play the animation.
    :param int y: The y coordinate of the location to play the animation.
    :param int z: The z coordinate of the location to play the animation.
    :param int stage: Stage from 0-9 in the breaking animation.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar x:
    :ivar y:
    :ivar z:
    :ivar stage:
    """

    id = 0x09

    def __init__(self, entity_id: int, x: int, y: int, z: int, stage: int):
        super().__init__()

        self.entity_id = entity_id
        self.x, self.y, self.z = x, y, z
        self.stage = stage

    def pack(self) -> Buffer:
        return Buffer().write_varint(self.entity_id).write_position(self.x, self.y, self.z).write("b", self.stage)


# vvv not confident about this one, pls check :) -emerald
class PlayAnimationServerBound(ServerBoundPacket):
    """Sent when a client's arm swings. (Client -> Server)

    :param int hand: Either main hand (0) or offhand (1).
    :ivar int id: Unique packet ID.
    :ivar hand:
    """

    id = 0x2C

    def __init__(self, hand: int):
        super().__init__()

        self.hand = hand

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayAnimationServerBound:
        return cls(buf.read_varint())


class PlayOpenBook(ClientBoundPacket):
    """Sent when a player right clicks a signed book. (Server -> Client)

    :param int hand: The hand used, either main (0) or offhand (1).
    :ivar int id: Unique packet ID.
    :ivar hand:
    """

    id = 0x2D

    def __init__(self, hand: int) -> None:
        super().__init__()

        self.hand = hand

    def pack(self) -> Buffer():
        return Buffer().write_varint(self.hand)
