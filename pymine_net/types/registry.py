from typing import Any, Mapping, Sequence, Union

__all__ = ("Registry",)


class Registry:
    """Stores various Minecraft data like block types, block states, particles, fluids, entities, and more."""

    def __init__(
        self,
        data: Union[Mapping, Sequence],
        data_reversed: Mapping = None,
    ):
        """
        Makes a doubly hashed map, providing O(1) lookups for both keys and values.

        If data_reversed is specified, we use it for the reverse map instead of autogenerating
        one from data  by simply swapping keys and values.

        If data is given as an iterable, we treat the positions as IDs (keys) and the elements as values.
        """
        if data_reversed is not None and not isinstance(data_reversed, Mapping):
            raise TypeError(f"data_reversed must be a Mapping, got {type(data_reversed)}.")

        if isinstance(data, Mapping):
            self.data = dict(data)
        elif isinstance(data, Sequence):
            self.data = {v: i for i, v in enumerate(data)}
        else:
            raise TypeError(f"Can't make registry from {type(data)}, must be Sequence/Mapping.")

        # Generate reverse mapping if it wasn't passed directly
        if data_reversed is None:
            self.data_reversed = {v: k for k, v in self.data.items()}
        else:
            self.data_reversed = data_reversed

    def encode(self, key: Any) -> Any:
        """Key -> value, most likely an identifier to an integer."""

        return self.data[key]

    def decode(self, value: Any) -> Any:
        """Value -> key, most likely a numeric id to a string identifier."""

        return self.data_reversed[value]
