"""Contains packets that are related to particles."""

from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket

__all__ = ("PlayParticle",)


class PlayParticle(ClientBoundPacket):
    """Sent by server to make the client display particles. (Server -> Client)

    :param int particle_id: ID of the particle.
    :param bool long_distance: If true, particle distance increases to 65536 from 256.
    :param int x: X coordinate of the particle.
    :param int y: Y coordinate of the particle.
    :param int z: Z coordinate of the particle.
    :param float particle_data: Particle data.
    :param int particle_count: How many particles to display.
    :param dict data: More particle data.
    :ivar int id: Unique packet ID.
    :ivar particle_id:
    :ivar long_distance:
    :ivar x:
    :ivar y:
    :ivar z:
    :ivar particle_data:
    :ivar particle_count:
    :ivar data:
    """

    id = 0x24

    def __init__(
        self,
        particle_id: int,
        long_distance: bool,
        x: float,
        y: float,
        z: float,
        offset_x: float,
        offset_y: float,
        offset_z: float,
        particle_data: float,
        particle_count: int,
        data: dict,
    ):
        super().__init__()

        self.part_id = particle_id
        self.long_dist = long_distance
        self.x = x
        self.y = y
        self.z = z
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z
        self.particle_data = particle_data
        self.particle_count = particle_count
        self.data = data

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write("i", self.part_id)
            .write("?", self.long_dist)
            .write("d", self.x)
            .write("d", self.y)
            .write("d", self.z)
            .write("f", self.offset_x)
            .write("f", self.offset_y)
            .write("f", self.offset_z)
            .write("f", self.particle_data)
            .write("i", self.particle_count)
            .write_particle(**self.data)
        )
