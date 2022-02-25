from typing import TypeVar

T = TypeVar("T")


class Vector3:
    __slots__ = ("x", "y", "z")

    def __init__(self, x: T, y: T, z: T):
        self.x = x
        self.y = y
        self.z = z


class Rotation:
    __slots__ = ("yaw", "pitch")

    def __init__(self, yaw: T, pitch: T):
        self.yaw = yaw
        self.pitch = pitch
