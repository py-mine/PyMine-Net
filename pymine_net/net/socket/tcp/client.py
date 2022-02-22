import socket
from typing import Union

from pymine_net.net.client import AbstractTCPClient
from pymine_net.net.socket.tcp.stream import SocketTCPStream
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = ("SocketTCPClient",)


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

    def read_packet(self) -> ClientBoundPacket:
        packet_length = self.stream.read_varint()
        return self._decode_packet(self.stream.read(packet_length))

    def write_packet(self, packet: ServerBoundPacket) -> None:
        self.stream.write(self._encode_packet(packet))
