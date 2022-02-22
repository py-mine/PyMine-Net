from typing import Dict, Tuple, Union
import socket

from pymine_net.net.server import AbstractTCPServer, AbstractTCPServerClient
from pymine_net.net.socket.tcp.stream import SocketTCPStream
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.packet_map import PacketMap


class SocketTCPServerClient(AbstractTCPServerClient):
    __slots__ = ("stream", "state", "compression_threshold")

    def __init__(self, stream: SocketTCPStream):
        super().__init__(stream)
        self.stream = stream


class SocketTCPServer(AbstractTCPServer):
    def __init__(self, host: str, port: int, protocol: Union[int, str], packet_map: PacketMap):
        super().__init__(host, port, protocol, packet_map)

        self.connected_clients: Dict[Tuple[str, int], SocketTCPServerClient] = {}

        self.sock: socket.socket = None

    async def run(self) -> None:
        self.server = socket.create_server((self.host, self.port))

    async def stop(self) -> None:
        self.server.close()

    def read_packet(self, client: SocketTCPServerClient) -> ServerBoundPacket:
        length = client.stream.read_varint()
        return self._decode_packet(client, client.stream.read(length))
        
    async def write_packet(self, client: SocketTCPServerClient, packet: ClientBoundPacket) -> None:
        client.stream.write(self._encode_packet(packet, client.compression_threshold))
