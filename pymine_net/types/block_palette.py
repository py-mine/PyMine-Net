from abc import ABC, abstractmethod


class Palette(ABC):
    @abstractmethod
    def get_bits_per_block(self) -> int:
        pass

    @abstractmethod
    def encode(self, block: str, props: dict = None) -> int:
        pass

    @abstractmethod
    def decode(self, state: int) -> dict:
        pass
