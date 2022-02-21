"""Contains packets related to entities."""

from __future__ import annotations

from typing import List, Tuple

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket

__all__ = ("PlayExplosion",)


class PlayExplosion(ClientBoundPacket):
    """Sent when an explosion occurs (creepers, TNT, and ghast fireballs). (Server -> Client)
    
    :param float x: The x coordinate of the explosion.
    :param float y: The y coordinate of the explosion.
    :param float z: The z coordinate of the explosion.
    :param float strength: Strength of the explosion, will summon a minecraft:explosion_emitter particle if >=2.0 else a minecraft:explosion particle.
    :param List[Tuple[int, int, int]] records: Array of bytes containing the coordinates of the blocks to destroy relative to the explosion's coordinates.
    :param float pmx: Velocity to add to the player's motion in the x axis due to the explosion.
    :param float pmy: Velocity to add to the player's motion in the y axis due to the explosion.
    :param float pmz: Velocity to add to the player's motion in the z axis due to the explosion.
    :ivar int id:
    :ivar x:
    :ivar y:
    :ivar z:
    :ivar strength:
    :ivar records:
    :ivar pmx:
    :ivar pmy:
    :ivar pmz:
    """

    id = 0x1C

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        strength: float,
        records: List[Tuple[int, int, int]],
        pmx: float,
        pmy: float,
        pmz: float,
    ):
        super().__init__()

        self.x = x
        self.y = y
        self.z = z
        self.strength = strength
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
            .write("i", len(self.records))
        )

        for rx, ry, rz in self.records:
            buf.write_byte(rx).write_byte(ry).write_byte(rz)
        
        return buf.write("f", self.pmx).write("f", self.pmy).write("f", self.pmz)
