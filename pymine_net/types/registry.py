from typing import Dict, Generic, Iterable, Mapping, Optional, TypeVar, Union, cast, overload

K = TypeVar("K")
V = TypeVar("V")

__all__ = ("Registry",)


class Registry(Generic[K, V]):
    """Stores various Minecraft data like block types, block states, particles, fluids, entities, and more."""

    data: Dict[K, V]
    data_reversed: Dict[V, K]

    @overload
    def __init__(
        self,
        data: Iterable[V],
        data_reversed: Optional[Iterable[V]] = None,
    ):
        ...

    @overload
    def __init__(
        self,
        data: Mapping[K, V],
        data_reversed: Optional[Mapping[V, K]] = None,
    ):
        ...

    def __init__(
        self,
        data: Union[Iterable[V], Mapping[K, V]],
        data_reversed: Optional[Union[Iterable[V], Mapping[V, K]]] = None,
    ):
        if isinstance(data, Mapping):
            data = cast(Mapping[K, V], data)
            self.data = dict(data)
            if data_reversed is None:
                self.data_reversed = {v: k for k, v in data.items()}
            else:
                data_reversed = cast(Mapping[V, K], data_reversed)
                self.data_reversed = dict(data_reversed)
        # When we get an iterable, we want to treat the positions as the
        # IDs for the values and the elements as keys.
        elif isinstance(data, (list, tuple)):
            self.data = {v: i for i, v in enumerate(data)}
            self.data_reversed = data
        else:
            raise TypeError(f"Can't make registry from {type(data)}, must be Iterable/Mapping.")

    def encode(self, key: K) -> V:
        """Key -> value, most likely an identifier to an integer."""

        return self.data[key]

    def decode(self, value: V) -> K:
        """Value -> key, most likely a numeric id to a string identifier."""

        return self.data_reversed[value]
