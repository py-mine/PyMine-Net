"""Contains packets related to command blocks."""

from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = (
    "PlayUpdateCommandBlock",
    "PlayUpdateCommandBlockMinecart",
)


class PlayUpdateCommandBlock(ServerBoundPacket):
    """Used when a client updates a command block. (Client -> Server)

    :param int x: The x coordinate of the command block.
    :param int y: The y coordinate of the command block.
    :param int z: The z coordinate of the command block.
    :param str command: The command text in the command block.
    :param int mode: The mode which the command block is in. Either sequence (0), auto (1), or redstone (2).
    :param int flags: Other flags, see here: https://wiki.vg/Protocol#Update_Command_Block.
    :ivar int id: Unique packet ID.
    :ivar x:
    :ivar y:
    :ivar z:
    :ivar command:
    :ivar mode:
    :ivar flags:
    """

    id = 0x26

    def __init__(self, x: int, y: int, z: int, command: str, mode: int, flags: int):
        super().__init__()

        self.x, self.y, self.z = x, y, z
        self.command = command
        self.mode = mode
        self.flags = flags

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayUpdateCommandBlock:
        return cls(buf.read_position(), buf.read_string(), buf.read_varint(), buf.read("b"))


class PlayUpdateCommandBlockMinecart(ServerBoundPacket):
    """Sent when the client updates a command block minecart. (Client -> Server)

    :param int entity_id: The ID of the entity (the minecart).
    :param str command: The command text in the command block.
    :param bool track_output: Whether output from the last command is saved.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar command:
    :ivar track_output:
    """

    id = 0x27

    def __init__(self, entity_id: int, command: str, track_output: bool):
        super().__init__()

        self.entity_id = entity_id
        self.command = command
        self.track_output = track_output

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayUpdateCommandBlockMinecart:
        return cls(buf.read_varint(), buf.read_string(), buf.read("?"))
