"""Contains packets related to the in-game map item."""

from __future__ import annotations

from typing import List, Optional, Tuple

from pymine_net.types.buffer import Buffer
from pymine_net.types.chat import Chat
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = ("PlayMapData",)


class PlayMapData(ClientBoundPacket):
    """Updates a rectangular area on a map item. (Server -> Client)
    
    :param int map_id: ID of the map to be modified.
    :param int scale: Zoom of the map (0 fully zoomed in - 4 fully zoomed out).
    :param bool locked: Whether the map has been locked in a cartography table or not.
    :param bool tracking_pos: Whether the player and other icons are shown on the map.
    :param List[Tuple[int, int, int, int, bool, Optional[Chat]]] icons: List of icons shown on the map.
    :param int columns: Number of columns being updated.
    :param Optional[int] rows: Number of rows being updated, only if columns > 0.
    :param Optional[int] x: X offset of the westernmost column, only if columns > 0.
    :param Optional[int] z: Z offset of the northernmost row, only if columns > 0.
    :param bytes data: The map data, see https://minecraft.fandom.com/wiki/Map_item_format.
    :ivar int id:
    :ivar map_id:
    :ivar scale:
    :ivar locked:
    :ivar tracking_pos:
    :ivar icons:
    :ivar columns:
    :ivar rows:
    :ivar x:
    :ivar z:
    :ivar data:
    """

    id = 0x27

    def __init__(
        self,
        map_id: int,
        scale: int,
        locked: bool,
        tracking_pos: bool,
        icons: List[Tuple[int, int, int, int, bool, Optional[Chat]]],
        columns: int,
        rows: int = None,
        x: int = None,
        z: int = None,
        data: bytes = None,
    ):
        super().__init__()

        self.map_id = map_id
        self.scale = scale
        self.tracking_pos = tracking_pos
        self.locked = locked
        self.icons = icons
        self.columns = columns
        self.rows = rows
        self.x = x
        self.z = z
        self.data = data

    def pack(self) -> Buffer:
        buf = (
            Buffer()
            .write_varint(self.map_id)
            .write_byte(self.scale)
            .write("?", self.locked)
            .write("?", self.tracking_pos)
            .write_varint(len(self.icons))
        )

        for (icon_type, x, z, direction, display_name) in self.icons:
            (
                buf
                .write_varint(icon_type)
                .write_byte(x)
                .write_byte(z)
                .write_byte(direction)
                .write_optional(buf.write_chat, display_name)
            )

        buf.write("B", self.columns)

        if len(self.columns) < 1:
            return buf

        return buf.write("B", self.rows).write_byte(self.x).write_byte(self.y).write_varint(len(self.data)).write_bytes(self.data)
