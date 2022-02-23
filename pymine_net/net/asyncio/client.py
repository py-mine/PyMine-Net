import asyncio
from typing import Union

from pymine_net.net.asyncio.stream import AsyncTCPStream
from pymine_net.net.client import AbstractTCPClient
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.packet_map import PacketMap

__all__ = ("AsyncTCPClient",)


class AsyncTCPClient(AbstractTCPClient):
    """An async connection over a TCP socket for reading + writing Minecraft packets."""

    def __init__(self, host: str, port: int, protocol: Union[int, str], packet_map: PacketMap):
        super().__init__(host, port, protocol, packet_map)

        self.stream: AsyncTCPStream = None

    async def connect(self) -> None:
        _, writer = await asyncio.open_connection(self.host, self.port)
        self.stream = AsyncTCPStream(writer)

    async def close(self) -> None:
        self.stream.close()
        await self.stream.wait_closed()

    async def read_packet(self) -> ClientBoundPacket:
        packet_length = await self.stream.read_varint()
        return self._decode_packet(await self.stream.readexactly(packet_length))

    async def write_packet(self, packet: ServerBoundPacket) -> None:
        self.stream.write(self._encode_packet(packet))
        await self.stream.drain()
