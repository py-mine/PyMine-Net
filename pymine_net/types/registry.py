from typing import TYPE_CHECKING, Any, Mapping, Optional, Sequence

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("Registry",)


class Registry:
    """Stores various Minecraft data like block types, block states, particles, fluids, entities, and more."""

    def __init__(
        self,
        data: Mapping,
        data_reversed: Optional[Mapping] = None,
    ):
        """
        Makes a doubly hashed map, providing O(1) lookups for both keys and values.

        If data_reversed is specified, we use it for the reverse map instead of autogenerating
        one from data  by simply swapping keys and values.
        """
        if data_reversed is not None and not isinstance(data_reversed, Mapping):
            raise TypeError(f"data_reversed must be a Mapping, got {type(data_reversed)}.")

        if isinstance(data, Mapping):
            self.data = dict(data)
        else:
            raise TypeError(f"Can't make registry from {type(data)}, must be Sequence/Mapping.")

        # Generate reverse mapping if it wasn't passed directly
        if data_reversed is None:
            self.data_reversed = {v: k for k, v in self.data.items()}
        else:
            self.data_reversed = data_reversed

    @classmethod
    def from_sequence(cls, seq: Sequence, reversed_data: Optional[Mapping] = None) -> Self:
        """
        Initialize the registry from a sequence, using it's positions (indices)
        as the values (often useful with things like numeric block IDs, etc.)
        and it's elements as the keys.

        If reversed_data is passed, we simply pass it over to __init__.
        """
        return cls({v: i for i, v in enumerate(seq)}, reversed_data)

    def encode(self, key: Any) -> Any:
        """Key -> value, most likely an identifier to an integer."""

        return self.data[key]

    def decode(self, value: Any) -> Any:
        """Value -> key, most likely a numeric id to a string identifier."""

        return self.data_reversed[value]
