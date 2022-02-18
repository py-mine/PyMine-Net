from abc import ABC, abstractmethod

__all__ = ("BlockPalette",)


class BlockPalette(ABC):
    @abstractmethod
    def get_bits_per_block(self) -> int:
        pass

    @abstractmethod
    def encode(self, block: str, props: dict = None) -> int:
        pass

    @abstractmethod
    def decode(self, state: int) -> dict:
        pass
