import selectors
import socket
from typing import Dict, Tuple, Union

from pymine_net.net.server import AbstractTCPServer, AbstractTCPServerClient
from pymine_net.net.socket.tcp.stream import SocketTCPStream
from pymine_net.strict_abc import abstract
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
        self.selector = selectors.DefaultSelector()
        self.running = False

    async def run(self) -> None:
        self.sock = socket.socket()
        self.sock.bind((self.host, self.port))
        self.sock.listen(100)
        self.sock.setblocking(False)

        self.selector.register(self.sock, selectors.EVENT_READ, self._client_connected_cb)

        while self.running:
            for key, mask in self.selector.select():
                if not self.running:
                    break

                key.data(key.fileobj, mask)

    async def stop(self) -> None:
        self.server.close()

    def read_packet(self, client: SocketTCPServerClient) -> ServerBoundPacket:
        length = client.stream.read_varint()
        return self._decode_packet(client, client.stream.read(length))

    def write_packet(self, client: SocketTCPServerClient, packet: ClientBoundPacket) -> None:
        client.stream.write(self._encode_packet(packet, client.compression_threshold))

    def _client_connected_cb(self, sock: socket.socket, mask: selectors._EventMask) -> None:
        connection, address = sock.accept()
        connection.setblocking(False)
        self.selector.register(connection, selectors.EVENT_READ, self._connection_update_cb)
        self.connected_clients[address] = SocketTCPServerClient(SocketTCPStream(connection))

    def _connection_update_cb(self, connection: socket.socket, mask: selectors._EventMask) -> None:
        client = self.connected_clients[connection.getpeername()]
        self.connection_update(client, self.read_packet(client))

    @abstract
    def incoming_packet(self, client: SocketTCPServerClient, packet: ServerBoundPacket) -> None:
        pass
