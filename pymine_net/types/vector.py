from typing import Generic, TypeVar

T_Numeric = TypeVar("T_Numeric", bound=float)


class Vector3(Generic[T_Numeric]):
    """
    Stores three numeric values: x, y, z.
    - Used for position and movement data in the Player class.
    """
    __slots__ = ("x", "y", "z")

    def __init__(self, x: T_Numeric, y: T_Numeric, z: T_Numeric):
        self.x = x
        self.y = y
        self.z = z


class Rotation(Generic[T_Numeric]):
    """
    Stores the pitch and yaw values of a rotation.
    - Used for storing rotation data in the Player class.
    """
    __slots__ = ("yaw", "pitch")

    def __init__(self, yaw: T_Numeric, pitch: T_Numeric):
        self.yaw = yaw
        self.pitch = pitch
