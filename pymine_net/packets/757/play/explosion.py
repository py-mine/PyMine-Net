"""Contains packets related to entities."""

from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = ("PlayExplosion",)


class PlayExplosion(ClientBoundPacket):
    """Sent when an explosion occurs (creepers, TNT, and ghast fireballs).                          Each block in Records is set to air. Coordinates for each axis in record is int(X) + record. (Server -> Client)"""

    id = 0x1C

    def __init__(
        self,
        x: int,
        y: int,
        z: int,
        strength: int,
        record_count: int,
        records: list,
        pmx: int,
        pmy: int,
        pmz: int,
    ) -> None:
        super().__init__()

        self.x, self.y, self.z = x, y, z
        self.strength = strength
        self.record_count = record_count
        self.records = records
        self.pmx = pmx
        self.pmy = pmy
        self.pmz = pmz

    def pack(self) -> Buffer:
        return (
            Buffer.write("f", self.x)
            + Buffer.write("f", self.y)
            + Buffer.write("f", self.z)
            + Buffer.write("f", self.strength)
            + Buffer.write("i", self.record_count)
            + b"".join([Buffer.write("b", r) for r in self.records])
            + Buffer.write("f", self.pmx)
            + Buffer.write("f", self.pmy)
            + Buffer.write("f", self.pmz)
        )
