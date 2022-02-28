import zlib
from abc import abstractmethod
from typing import Dict, Tuple, Type, Union

from pymine_net.enums import GameState, PacketDirection
from pymine_net.errors import UnknownPacketIdError
from pymine_net.net.stream import AbstractTCPStream
from pymine_net.strict_abc import StrictABC
from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.packet_map import PacketMap


class AbstractProtocolServerClient(StrictABC):
    __slots__ = ("stream", "packet_map", "state", "compression_threshold")

    def __init__(self, stream: AbstractTCPStream, packet_map: PacketMap):
        self.stream = stream
        self.packet_map = packet_map
        self.state = GameState.HANDSHAKING
        self.compression_threshold = -1

    def _encode_packet(self, packet: ClientBoundPacket) -> Buffer:
        """Encodes and (if necessary) compresses a ClientBoundPacket."""

        buf = Buffer().write_varint(packet.id).extend(packet.pack())

        if self.compression_threshold >= 1:
            if len(buf) >= self.compression_threshold:
                buf = Buffer().write_varint(len(buf)).extend(zlib.compress(buf))
            else:
                buf = Buffer().write_varint(0).extend(buf)

        buf = Buffer().write_varint(len(buf)).extend(buf)
        return buf

    def _decode_packet(self, buf: Buffer) -> ServerBoundPacket:
        # decompress packet if necessary
        if self.compression_threshold >= 0:
            uncompressed_length = buf.read_varint()

            if uncompressed_length > 0:
                buf = Buffer(zlib.decompress(buf.read_bytes()))

        packet_id = buf.read_varint()

        # attempt to get packet class from given state and packet id
        try:
            packet_class: Type[ClientBoundPacket] = self.packet_map[
                PacketDirection.SERVERBOUND, self.state, packet_id
            ]
        except KeyError:
            raise UnknownPacketIdError(
                self.packet_map.protocol, self.state, packet_id, PacketDirection.SERVERBOUND
            )

        return packet_class.unpack(buf)

    @abstractmethod
    def read_packet(self) -> ServerBoundPacket:
        pass

    @abstractmethod
    def write_packet(self, packet: ClientBoundPacket) -> None:
        pass


class AbstractProtocolServer(StrictABC):
    """Abstract class for a TCP server that handles Minecraft packets."""

    def __init__(self, host: str, port: int, protocol: Union[int, str], packet_map: PacketMap):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.packet_map = packet_map

        self.connected_clients: Dict[Tuple[str, int], AbstractProtocolServerClient] = {}

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
