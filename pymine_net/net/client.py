import zlib
from typing import Type, Union
from abc import abstractmethod

from pymine_net.enums import GameState, PacketDirection
from pymine_net.errors import UnknownPacketIdError
from pymine_net.strict_abc import StrictABC
from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.packet_map import PacketMap


class AbstractProtocolClient(StrictABC):
    """Abstract class for a connection over a TCP socket for reading + writing Minecraft packets."""

    def __init__(self, host: str, port: int, protocol: Union[int, str], packet_map: PacketMap):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.packet_map = packet_map

        self.state = GameState.HANDSHAKING
        self.compression_threshold = -1

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @staticmethod
    def _encode_packet(packet: ServerBoundPacket, compression_threshold: int = -1) -> Buffer:
        """Encodes and (if necessary) compresses a ServerBoundPacket."""

        buf = Buffer().write_varint(packet.id).extend(packet.pack())

        if compression_threshold >= 1:
            if len(buf) >= compression_threshold:
                buf = Buffer().write_varint(len(buf)).extend(zlib.compress(buf))
            else:
                buf = Buffer().write_varint(0).extend(buf)

        return Buffer().write_varint(len(buf)).extend(buf)

    def _decode_packet(self, buf: Buffer) -> ClientBoundPacket:
        # decompress packet if necessary
        if self.compression_threshold >= 0:
            uncompressed_length = buf.read_varint()

            if uncompressed_length > 0:
                buf = Buffer(zlib.decompress(buf.read_bytes()))

        packet_id = buf.read_varint()

        # attempt to get packet class from given state and packet id
        try:
            packet_class: Type[ClientBoundPacket] = self.packet_map[
                PacketDirection.CLIENTBOUND, self.state, packet_id
            ]
        except KeyError:
            raise UnknownPacketIdError(None, self.state, packet_id, PacketDirection.CLIENTBOUND)

        return packet_class.unpack(buf)

    @abstractmethod
    def read_packet(self) -> ClientBoundPacket:
        pass

    @abstractmethod
    def write_packet(self, packet: ServerBoundPacket) -> None:
        pass
