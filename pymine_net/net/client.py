from typing import Type, Union
import zlib
from pymine_net.enums import GameState, PacketDirection
from pymine_net.errors import UnknownPacketIdError
from pymine_net.packets import load_packet_map
from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.strict_abc import StrictABC, abstract

class AbstractTCPClient(StrictABC):
    """Abstract class for a connection over a TCP socket for reading + writing Minecraft packets."""

    def __init__(self, host: str, port: int, protocol: Union[int, str]):
        self.host = host
        self.port = port

        self.packet_map = load_packet_map(protocol)
        
        self.state = GameState.HANDSHAKING
        self.compression_threshold = -1

    @abstract
    def connect(self) -> None:
        pass

    @abstract
    def close(self) -> None:
        pass
    
    @staticmethod
    def encode_packet(packet: ClientBoundPacket, compression_threshold: int = -1) -> Buffer:
        """Encodes and (if necessary) compresses a ClientBoundPacket."""

        buf = Buffer().write_varint(packet.id).extend(packet.pack())

        if compression_threshold >= 1:
            if len(buf) >= compression_threshold:
                buf = Buffer().write_varint(len(buf)).extend(zlib.compress(buf))
            else:
                buf = Buffer().write_varint(0).extend(buf)

        return Buffer().write_varint(len(buf)).extend(buf)

    def decode_packet(self, buf: Buffer) -> ClientBoundPacket:
        # decompress packet if necessary
        if self.compression_threshold >= 0:
            uncompressed_length = buf.read_varint()

            if uncompressed_length > 0:
                buf = Buffer(zlib.decompress(buf.read_bytes()))

        packet_id = buf.read_varint()

        # attempt to get packet class from given state and packet id
        try:
            packet_class: Type[ClientBoundPacket] = self.packet_map[PacketDirection.CLIENTBOUND, self.state, packet_id]
        except KeyError:
            raise UnknownPacketIdError(None, self.state, packet_id, PacketDirection.CLIENTBOUND)

        return packet_class.unpack(buf)

    @abstract
    def read_packet_length(self) -> int:
        pass

    @abstract
    def read_packet(self) -> ClientBoundPacket:
        pass

    @abstract
    def write_packet(self, packet: ServerBoundPacket) -> None:
        pass
