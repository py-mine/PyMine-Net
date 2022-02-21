from enum import Enum, IntEnum

__all__ = ("GameState", "Direction", "Pose", "EntityModifier")


class PacketDirection(Enum):
    CLIENTBOUND = "CLIENT-BOUND"
    SERVERBOUND = "SERVER-BOUND"


class GameState(IntEnum):
    HANDSHAKING = 0
    STATUS = 1
    LOGIN = 2
    PLAY = 3


class Direction(IntEnum):
    DOWN = 0
    UP = 1
    NORTH = 2
    SOUTH = 3
    WEST = 4
    EAST = 5


class Pose(IntEnum):
    STANDING = 0
    FALL_FLYING = 1
    SLEEPING = 2
    SWIMMING = 3
    SPIN_ATTACK = 4
    SNEAKING = 5
    DYING = 6


class EntityModifier(IntEnum):
    MODIFY = 0  # add / subtract amount
    MODIFY_PERCENT = 1  # add / subtract amount percent of the current value
    MODIFY_MULTIPLY_PERCENT = 2  # multiply by percent amount
