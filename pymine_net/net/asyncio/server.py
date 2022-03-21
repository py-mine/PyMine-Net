import asyncio
from abc import abstractmethod
from typing import Dict, Tuple, Union

from pymine_net.net.asyncio.stream import AsyncTCPStream
from pymine_net.net.server import AbstractProtocolServer, AbstractProtocolServerClient
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.packet_map import PacketMap

__all__ = ("AsyncProtocolServerClient", "AsyncProtocolServer")


class AsyncProtocolServerClient(AbstractProtocolServerClient):
    def __init__(self, stream: AsyncTCPStream, packet_map: PacketMap):
        super().__init__(stream, packet_map)
        self.stream = stream  # redefine this cause typehints

    async def read_packet(self) -> ServerBoundPacket:
        length = await self.stream.read_varint()
        return self._decode_packet(await self.stream.readexactly(length))

    async def write_packet(self, packet: ClientBoundPacket) -> None:
        self.stream.write(self._encode_packet(packet))
        await self.stream.drain()


class AsyncProtocolServer(AbstractProtocolServer):
    def __init__(self, host: str, port: int, protocol: Union[int, str], packet_map: PacketMap):
        super().__init__(host, port, protocol, packet_map)

        self.connected_clients: Dict[Tuple[str, int], AsyncProtocolServerClient] = {}

        # We type-ignore this assignment since we don't expect it to stay as None
        # it should be set in run function which is expected to be ran after init
        # this avoids further type-ignores or casts whenever it'd be used, to tell
        # type checker that it won't actually be None.
        self.server: asyncio.AbstractServer = None  # type: ignore

    async def run(self) -> None:
        self.server = await asyncio.start_server(self._client_connected_cb, self.host, self.port)

    async def close(self) -> None:
        self.server.close()
        await self.server.wait_closed()

    async def _client_connected_cb(
        self, _: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        client = AsyncProtocolServerClient(AsyncTCPStream(writer), self.packet_map)

        self.connected_clients[client.stream.remote] = client

        await self.new_client_connected(client)

    @abstractmethod
    async def new_client_connected(self, client: AsyncProtocolServerClient) -> None:
        pass
