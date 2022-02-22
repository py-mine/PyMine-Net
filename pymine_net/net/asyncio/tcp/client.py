import asyncio
import struct
from typing import Union

from pymine_net.net.asyncio.tcp.stream import AsyncTCPStream
from pymine_net.net.client import AbstractTCPClient
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket


class AsyncTCPClient(AbstractTCPClient):
    """An async connection over a TCP socket for reading + writing Minecraft packets."""

    def __init__(self, host: str, port: int, protocol: Union[int, str]):
        super().__init__(host, port, protocol)

        self.stream: AsyncTCPStream = None

    async def connect(self) -> None:
        _, writer = await asyncio.open_connection(self.host, self.port)
        self.stream = AsyncTCPStream(writer)

    async def close(self) -> None:
        self.stream.close()
        await self.stream.wait_closed()

    async def read_packet_length(self) -> int:
        value = 0

        for i in range(10):
            byte = struct.unpack(">B", await self.stream.readexactly(1))
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

    async def read_packet(self) -> ClientBoundPacket:
        packet_length = await self.read_packet_length()
        return self.decode_packet(await self.stream.readexactly(packet_length))

    async def write_packet(self, packet: ServerBoundPacket) -> None:
        await self.stream.write(self.encode_packet(packet))
