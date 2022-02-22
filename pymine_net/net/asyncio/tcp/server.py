
import asyncio
from typing import Dict, Tuple, Union
from pymine_net.net.asyncio.tcp.stream import AsyncTCPStream
from pymine_net.net.server import AbstractTCPServer, AbstractTCPServerClient
from pymine_net.strict_abc import abstract
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.packet_map import PacketMap


class AsyncTCPServerClient(AbstractTCPServerClient):
    __slots__ = ("stream", "state", "compression_threshold")

    def __init__(self, stream: AsyncTCPStream):
        super().__init__(stream)
        self.stream = stream


class AsyncTCPServer(AbstractTCPServer):
    def __init__(self, host: str, port: int, protocol: Union[int, str], packet_map: PacketMap):
        super().__init__(host, port, protocol, packet_map)

        self.connected_clients: Dict[Tuple[str, int], AsyncTCPServerClient] = {}

        self.server: asyncio.AbstractServer = None

    async def run(self) -> None:
        self.server = await asyncio.start_server()

    async def stop(self) -> None:
        self.server.close()
        await self.server.wait_closed()

    async def read_packet(self, client: AsyncTCPServerClient) -> ServerBoundPacket:
        length = await client.stream.read_varint()
        return self._decode_packet(client, await client.stream.readexactly(length))
        
    async def write_packet(self, client: AsyncTCPServerClient, packet: ClientBoundPacket) -> None:
        client.stream.write(self._encode_packet(packet, client.compression_threshold))
        await client.stream.drain()

    async def _client_connected_cb(self, _: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        client = AsyncTCPServerClient(AsyncTCPStream(writer))

        self.connected_clients[client.stream.remote] = client

        await self.new_client_connected(client)

    @abstract
    async def new_client_connected(self, client: AsyncTCPServerClient) -> None:
        pass
