from strict_abc import StrictABC, abstract

__all__ = ("BlockPalette",)


class BlockPalette(StrictABC):
    @abstract
    def get_bits_per_block(self) -> int:
        pass

    @abstract
    def encode(self, block: str, props: dict = None) -> int:
        pass

    @abstract
    def decode(self, state: int) -> dict:
        pass
