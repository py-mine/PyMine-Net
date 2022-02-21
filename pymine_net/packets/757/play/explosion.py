"""Contains packets related to entities."""

from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket

__all__ = ("PlayExplosion",)


class PlayExplosion(ClientBoundPacket):
    """Sent when an explosion occurs (creepers, TNT, and ghast fireballs). Each block in Records is set to air. Coordinates for each axis in record is int(X) + record. (Server -> Client)"""

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

        buf = (
            Buffer()
            .write("f", self.x)
            .write("f", self.y)
            .write("f", self.z)
            .write("f", self.strength)
            .write("i", self.record_count)
        )

        for r in self.records:
            buf.write("b", r)

        buf.write("f", self.pmx).write("f", self.pmy).write("f", self.pmz)
        return buf
