import struct
from asyncio import StreamWriter
from typing import Tuple, Union

from cryptography.hazmat.primitives.ciphers import Cipher

from pymine_net.net.stream import AbstractTCPStream
from pymine_net.types.buffer import Buffer

__all__ = ("AsyncTCPStream", "EncryptedAsyncTCPStream")


class AsyncTCPStream(AbstractTCPStream, StreamWriter):
    """Used for reading and writing from/to a connected client, merges functions of a StreamReader and StreamWriter.

    :param StreamReader reader: An asyncio.StreamReader instance.
    :param StreamWriter writer: An asyncio.StreamWriter instance.
    :ivar Tuple[str, int] remote: A tuple which stores the remote client's address and port.
    """

    def __init__(self, writer: StreamWriter):
        super().__init__(writer._transport, writer._protocol, writer._reader, writer._loop)

        self.remote: Tuple[str, int] = self.get_extra_info("peername")

    async def read(self, length: int = -1) -> Buffer:
        return Buffer(await self._reader.read(length))

    async def readline(self) -> Buffer:
        return Buffer(await self._reader.readline())

    async def readexactly(self, length: int) -> Buffer:
        return Buffer(await self._reader.readexactly(length))

    async def readuntil(self, separator: bytes = b"\n") -> Buffer:
        return Buffer(await self._reader.readuntil(separator))

    async def read_varint(self) -> int:
        value = 0

        for i in range(10):
            byte = struct.unpack(">B", await self.readexactly(1))
            value |= (byte & 0x7F) << 7 * i

            if not byte & 0x80:
                break

        if value & (1 << 31):
            value -= 1 << 32

        value_max = (1 << (32 - 1)) - 1
        value_min = -1 << (32 - 1)

        if not (value_min <= value <= value_max):
            raise ValueError(
                f"Value doesn't fit in given range: {value_min} <= {value} < {value_max}"
            )

        return value


class EncryptedAsyncTCPStream(AsyncTCPStream):
    """An encrypted version of an AsyncTCPStream, automatically encrypts and decrypts outgoing and incoming data.

    :param AsyncTCPStream stream: The original, stream-compatible object.
    :param Cipher cipher: The cipher instance, used to encrypt + decrypt data.
    :ivar _CipherContext decryptor: Description of parameter `_CipherContext`.
    :ivar _CipherContext encryptor: Description of parameter `_CipherContext`.
    """

    def __init__(self, stream: AsyncTCPStream, cipher: Cipher):
        super().__init__(stream)

        self.decryptor = cipher.decryptor()
        self.encryptor = cipher.encryptor()

    async def read(self, length: int = -1) -> Buffer:
        return Buffer(self.decryptor.update(await super().read(length)))

    async def readline(self) -> Buffer:
        return Buffer(self.decryptor.update(await super().readline()))

    async def readexactly(self, length: int) -> Buffer:
        return Buffer(self.decryptor.update(await super().readexactly(length)))

    async def readuntil(self, separator: bytes = b"\n") -> Buffer:
        return Buffer(self.decryptor.update(await super().readuntil(separator)))

    def write(self, data: Union[Buffer, bytes, bytearray]) -> None:
        super().write(self.encryptor.update(data))

    def writelines(self, data: Union[Buffer, bytes, bytearray]) -> None:
        super().writelines(self.encryptor.update(data))
