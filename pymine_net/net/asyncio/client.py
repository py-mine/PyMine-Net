import asyncio
from typing import Union

from pymine_net.net.asyncio.stream import AsyncTCPStream
from pymine_net.net.client import AbstractProtocolClient
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.packet_map import PacketMap

__all__ = ("AsyncProtocolClient",)


class AsyncProtocolClient(AbstractProtocolClient):
    """An async connection over a TCP socket for reading + writing Minecraft packets."""

    def __init__(self, host: str, port: int, protocol: Union[int, str], packet_map: PacketMap):
        super().__init__(host, port, protocol, packet_map)

        # We type-ignore this assignment since we don't expect it to stay as None
        # it should be set in connect function which is expected to be ran after init
        # this avoids further type-ignores or casts whenever it'd be used, to tell
        # type checker that it won't actually be None.
        self.stream: AsyncTCPStream = None  # type: ignore

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
