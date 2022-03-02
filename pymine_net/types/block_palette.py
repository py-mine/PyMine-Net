from abc import abstractmethod

from strict_abc import StrictABC

__all__ = ("BlockPalette",)


class BlockPalette(StrictABC):
    @abstractmethod
    def get_bits_per_block(self) -> int:
        pass

    @abstractmethod
    def encode(self, block: str, props: dict = None) -> int:
        pass

    @abstractmethod
    def decode(self, state: int) -> dict:
        pass
