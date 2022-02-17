from typing import Union

__all__ = ("Registry",)


class Registry:
    def __init__(self, data: Union[dict, list, tuple], data_reversed: Union[dict, list, tuple] = None):
        self.data_reversed = data_reversed

        if isinstance(data, dict):
            self.data = data

            if data_reversed is None:
                self.data_reversed = {v: k for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            self.data_reversed = data
            self.data = {v: i for i, v in enumerate(self.data_reversed)}
        else:
            raise TypeError(
                "Creating a registry from something other than a dict, tuple, or list isn't supported"
            )

    def encode(self, key: object) -> object:
        """Key -> value, most likely an identifier to an integer."""

        return self.data[key]

    def decode(self, value: object) -> object:
        """Value -> key, most likely a numeric id to a string identifier."""

        return self.data_reversed[value]
