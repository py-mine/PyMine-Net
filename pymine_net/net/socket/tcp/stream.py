import socket
import struct
from typing import Tuple, Union

from cryptography.hazmat.primitives.ciphers import Cipher

from pymine_net.net.stream import AbstractTCPStream
from pymine_net.types.buffer import Buffer

__all__ = ("SocketTCPStream", "EncryptedSocketTCPStream")


class SocketTCPStream(AbstractTCPStream, socket.socket):
    """Used for reading and writing from/to a connected client, wraps a socket.socket.

    :param socket.socket sock: A socket.socket instance.
    :ivar Tuple[str, int] remote: A tuple which stores the remote client's address and port.
    :ivar sock:
    """

    __slots__ = ("sock",)

    def __init__(self, sock: socket.socket):
        self.sock = sock
        
        self.remote: Tuple[str, int] = sock.getsockname()

    def read(self, length: int) -> bytearray:
        result = bytearray()

        while len(result) < length:
            read_bytes = self.sock.recv(length - len(result))

            if len(read_bytes) == 0:
                raise IOError("Server didn't respond with information!")

            result.extend(read_bytes)

        return result

    def write(self, data: bytes) -> None:
        self.sock.send(data)

    def close(self) -> None:
        self.sock.close()

    def read_varint(self) -> int:
        value = 0

        for i in range(10):
            byte = struct.unpack(">B", self.read(1))
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


class EncryptedSocketTCPStream(SocketTCPStream):
    """Used for reading and writing from/to a connected client, wraps a socket.socket.

    :param socket.socket sock: A socket.socket instance.
    :param Cipher cipher: The cipher instance, used to encrypt + decrypt data.
    :ivar Tuple[str, int] remote: A tuple which stores the remote client's address and port.
    :ivar sock:
    :ivar _CipherContext decryptor: Description of parameter `_CipherContext`.
    :ivar _CipherContext encryptor: Description of parameter `_CipherContext`.
    """

    def __init__(self, sock: socket.socket, cipher: Cipher):
        super().__init__(sock)

        self.decryptor = cipher.decryptor()
        self.encryptor = cipher.encryptor()

    def read(self, length: int) -> Buffer:
        return Buffer(self.decryptor.update(super().read(length)))

    def write(self, data: Union[Buffer, bytes, bytearray]) -> None:
        super().write(self.encryptor.update(data))
