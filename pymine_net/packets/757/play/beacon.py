"""Contains packets related to beacons."""

from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ServerBoundPacket

__all__ = ("PlaySetBeaconEffect",)


class PlaySetBeaconEffect(ServerBoundPacket):
    """Changes the effect of the current beacon. (Client -> Server)

    :param int primary_effect: Description of parameter `primary_effect`.
    :param int secondary_effect: Description of parameter `secondary_effect`.
    :ivar int id: Unique packet ID.
    :ivar primary_effect:
    :ivar secondary_effect:
    """

    id = 0x24

    def __init__(self, primary_effect: int, secondary_effect: int):
        super().__init__()

        self.primary_effect = primary_effect
        self.secondary_effect = secondary_effect

    @classmethod
    def unpack(cls, buf: Buffer) -> PlaySetBeaconEffect:
        return cls(buf.read_varint(), buf.read_varint())
