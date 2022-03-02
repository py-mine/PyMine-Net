from abc import abstractmethod

from strict_abc import StrictABC

__all__ = ("AbstractBlockPalette",)


class AbstractBlockPalette(StrictABC):
    """
    Used to encode/decode the types of Minecraft blocks to/from a compact format used when sending chunk data.
    - See: https://wiki.vg/Chunk_Format#Palettes
    - Currently unused because the Buffer implementation isn't complete
    """

    @abstractmethod
    def get_bits_per_block(self) -> int:
        pass

    @abstractmethod
    def encode(self, block: str, props: dict = None) -> int:
        pass

    @abstractmethod
    def decode(self, state: int) -> dict:
        pass
