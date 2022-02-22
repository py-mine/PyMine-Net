"""Contains LoginSetCompression which is technically part of the login process."""

from __future__ import annotations

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket

__all__ = ("LoginSetCompression",)


class LoginSetCompression(ClientBoundPacket):
    """While not directly related to login, this packet is sent by the server during the login process. (Server -> Client)

    :param int compression_threshold: Compression level of future packets, -1 to disable compression.
    :ivar int id: Unique packet ID.
    :ivar compression_threshold:
    """

    id = 0x03

    def __init__(self, compression_threshold: int = -1):
        super().__init__()

        self.compression_threshold = compression_threshold

    def pack(self) -> Buffer:
        return Buffer().write_varint(self.compression_threshold)

    @classmethod
    def unpack(cls, buf: Buffer) -> LoginSetCompression:
        return cls(buf.read_varint())
