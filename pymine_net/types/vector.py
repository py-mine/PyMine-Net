from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T", bound=float)


@dataclass(slots=True)
class Vector3(Generic[T]):
    """
    Stores three numeric values: x, y, z.
    - Used for position and movement data in the Player class.
    """

    x: T
    y: T
    z: T


@dataclass(slots=True)
class Rotation(Generic[T]):
    """
    Stores the pitch and yaw values of a rotation.
    - Used for storing rotation data in the Player class.
    """

    yaw: T
    pitch: T
