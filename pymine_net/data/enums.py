from enum import IntEnum


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
