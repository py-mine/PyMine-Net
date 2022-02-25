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


class MainHand(IntEnum):
    LEFT = 0
    RIGHT = 1


class ChatMode(IntEnum):
    ENABLED = 0
    COMMANDS_ONLY = 1
    HIDDEN = 2


class SkinPart(IntEnum):
    CAPE = 0x01
    JACKET = 0x02
    LEFT_SLEEVE = 0x04
    RIGHT_SLEEVE = 0x08
    LEFT_PANTS_LEG = 0x10
    RIGHT_PANTS_LEG = 0x20
    HAT = 0x40


class GameMode(IntEnum):
    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    SPECTATOR = 3


class PlayerInfoAction(IntEnum):
    ADD_PLAYER = 0
    UPDATE_GAMEMODE = 1
    UPDATE_LATENCY = 2
    UPDATE_DISPLAY_NAME = 3
    REMOVE_PLAYER = 4
