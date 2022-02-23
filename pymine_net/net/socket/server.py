import threading
import socket
from typing import Dict, List, Tuple, Union

from pymine_net.net.server import AbstractProtocolServer, AbstractProtocolServerClient
from pymine_net.net.socket.stream import SocketTCPStream
from pymine_net.strict_abc import abstract
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.packet_map import PacketMap


class SocketProtocolServerClient(AbstractProtocolServerClient):
    def __init__(self, stream: SocketTCPStream, packet_map: PacketMap):
        super().__init__(stream, packet_map)
        self.stream = stream  # redefine this cause tyephints

    def read_packet(self) -> ServerBoundPacket:
        length = self.stream.read_varint()
        return self._decode_packet(self.stream.read(length))

    def write_packet(self, packet: ClientBoundPacket) -> None:
        self.stream.write(self._encode_packet(packet))


class SocketProtocolServer(AbstractProtocolServer):
    def __init__(self, host: str, port: int, protocol: Union[int, str], packet_map: PacketMap):
        super().__init__(host, port, protocol, packet_map)

        self.connected_clients: Dict[Tuple[str, int], SocketProtocolServerClient] = {}

        self.sock: socket.socket = None
        self.threads: List[threading.Thread] = []
        self.running = False

    def run(self) -> None:
        self.running = True

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
            self.sock.bind((self.host, self.port))
            self.sock.listen(20)

            while self.running:
                connection, _ = self.sock.accept()
                self._client_connected_cb(connection)

    def close(self) -> None:
        self.sock.close()
        
        for thread in self.threads:
            thread.join(0.1)

    def _client_connected_cb(self, sock: socket.socket) -> None:
        client = SocketProtocolServerClient(SocketTCPStream(sock), self.packet_map)
        self.connected_clients[client.stream.remote] = client
        thread = threading.Thread(target=self._new_client_connected, args=(client,))
        self.threads.append(thread)
        thread.start()

    def _new_client_connected(self, client: SocketProtocolServerClient) -> None:
        with client.stream.sock:
            self.new_client_connected(client)

    @abstract
    def new_client_connected(self, client: SocketProtocolServerClient) -> None:
        pass
