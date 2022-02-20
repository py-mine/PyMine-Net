"""Contains packets related to server difficulty."""

from __future__ import annotations

from pymine.types.packet import ServerBoundPacket, ClientBoundPacket
from pymine.types.buffer import Buffer

__all__ = (
    "PlayServerDifficulty",
    "PlaySetDifficulty",
    "PlayLockDifficulty",
)


class PlayServerDifficulty(ClientBoundPacket):
    """Used by the server to update the difficulty in the client's menu. (Server -> Client)

    :param int difficulty: The difficulty level, see here: https://wiki.vg/Protocol#Server_Difficulty.
    :param bool locked: Whether the difficulty is locked or not.
    :ivar int id: Unique packet ID.
    :ivar difficulty:
    :ivar locked:
    """

    id = 0x0E

    def __init__(self, difficulty: int, locked: bool) -> None:
        super().__init__()

        self.difficulty = difficulty
        self.locked = locked

    def pack(self) -> Buffer:
        return Buffer.write("B", self.difficulty) + Buffer.write("?", self.locked)


class PlaySetDifficulty(ServerBoundPacket):
    """Used by the client to set difficulty. Not used normally. (Client -> Server)

    :param int new_difficulty: The new difficulty.
    :ivar int id: Unique packet ID.
    :ivar new_difficulty:
    """

    id = 0x02

    def __init__(self, new_difficulty: int) -> None:
        super().__init__()

        self.new_difficulty = new_difficulty

    @classmethod
    def unpack(cls, buf: Buffer) -> PlaySetDifficulty:
        return cls(buf.read("b"))


class PlayLockDifficulty(ServerBoundPacket):
    """Used to lock the difficulty. Only used on singleplayer. (Client -> Server)

    :param bool locked: Whether the difficulty is locked or not.
    :ivar int id: Unique packet ID.
    :ivar locked:
    """

    id = 0x10

    def __init__(self, locked: bool) -> None:
        super().__init__()

        self.locked = locked

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayLockDifficulty:
        return cls(buf.read("?"))
