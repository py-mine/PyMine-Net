from typing import TypeVar

T = TypeVar("T")


class Vector3:
    """
    Stores three numeric values: x, y, z.
    - Used for position and movement data in the Player class.
    """

    __slots__ = ("x", "y", "z")

    def __init__(self, x: T, y: T, z: T):
        self.x = x
        self.y = y
        self.z = z


class Rotation:
    """
    Stores the pitch and yaw values of a rotation.
    - Used for storing rotation data in the Player class.
    """

    __slots__ = ("yaw", "pitch")

    def __init__(self, yaw: T, pitch: T):
        self.yaw = yaw
        self.pitch = pitch
