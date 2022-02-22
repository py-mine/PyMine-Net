import socket
import struct
from typing import Union

from pymine_net.net.socket.tcp.stream import SocketTCPStream
from pymine_net.net.client import AbstractTCPClient
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket


class SocketTCPClient(AbstractTCPClient):
    """A connection over a TCP socket for reading + writing Minecraft packets."""

    def __init__(self, host: str, port: int, protocol: Union[int, str]):
        super().__init__(host, port, protocol)

        self.stream: SocketTCPStream = None

    def connect(self) -> None:
        sock = socket.create_connection((self.host, self.port))
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.stream = SocketTCPStream(sock)

    def close(self) -> None:
        self.stream.close()

    def read_packet_length(self) -> int:
        value = 0

        for i in range(10):
            byte = struct.unpack(">B", self.stream.read(1))
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

    def read_packet(self) -> ClientBoundPacket:
        packet_length = self.read_packet_length()
        return self.decode_packet(self.stream.read(packet_length))

    def write_packet(self, packet: ServerBoundPacket) -> None:
        self.stream.write(self.encode_packet(packet))