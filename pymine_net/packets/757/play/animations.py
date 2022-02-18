# A flexible and fast Minecraft server software written completely in Python.
# Copyright (C) 2021 PyMine

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Contains animation packets."""

from __future__ import annotations

from pymine.types.packet import Packet
from pymine.types.buffer import Buffer

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
