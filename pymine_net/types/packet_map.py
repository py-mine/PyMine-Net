from __future__ import annotations

from typing import Dict, List, Tuple, Type, Union
import zlib

from pymine_net.enums import GameState, PacketDirection
from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, Packet, ServerBoundPacket


class UnknownPacketIdError(Exception):
    def __init__(self, protocol: Union[str, int], state: GameState, packet_id: int, direction: PacketDirection):
        super().__init__(f"Unknown packet ID 0x{packet_id:02X} (protocol={protocol}, state={state.name}, {direction.value})")

        self.protocol = protocol
        self.state = state
        self.packet_id = packet_id
        self.direction = direction


class DuplicatePacketIdError(Exception):
    def __init__(self, protocol: Union[str, int], state: GameState, packet_id: int, direction: PacketDirection):
        super().__init__(
            f"Duplicate packet ID found (protocol={protocol}, state={state.name}, {direction}): 0x{packet_id:02X}"
        )

        self.protocol = protocol
        self.state = state
        self.packet_id = packet_id
        self.direction = direction


class StatePacketMap:
    """Stores a game state's packets"""

    def __init__(
        self,
        state: GameState,
        server_bound: Dict[int, Type[ServerBoundPacket]],
        client_bound: Dict[int, Type[ClientBoundPacket]],
    ):
        self.state = state
        self.server_bound = server_bound
        self.client_bound = client_bound

    @classmethod
    def from_list(
        cls, state: GameState, packets: List[Type[Packet]], *, check_duplicates: bool = False
    ) -> StatePacketMap:
        self = cls(
            state,
            {p.id: p for p in packets if issubclass(p, ServerBoundPacket)},
            {p.id: p for p in packets if issubclass(p, ClientBoundPacket)},
        )

        if check_duplicates:
            for packet_id in self.server_bound.keys():
                found = [
                    p for p in packets if p.id == packet_id and issubclass(p, ServerBoundPacket)
                ]

                if len(found) > 1:
                    raise DuplicatePacketIdError("unknown", state, packet_id, PacketDirection.SERVERBOUND)

            for packet_id in self.client_bound.keys():
                found = [
                    p for p in packets if p.id == packet_id and issubclass(p, ClientBoundPacket)
                ]

                if len(found) > 1:
                    raise DuplicatePacketIdError("unknown", state, packet_id, PacketDirection.CLIENTBOUND)

        return self


class PacketMap:
    """Stores a Minecraft protocol's packets"""

    def __init__(self, protocol: Union[str, int], packets: Dict[GameState, StatePacketMap]):
        self.protocol = protocol
        self.packets = packets

    def encode_packet(self, packet: ClientBoundPacket, compression_threshold: int = -1) -> Buffer:
        """Encodes and (if necessary) compresses a ClientBoundPacket."""

        buf = Buffer().write_varint(packet.id).extend(packet.pack())

        if compression_threshold >= 1:
            if len(buf) >= compression_threshold:
                buf = Buffer().write_varint(len(buf)).extend(zlib.compress(buf))
            else:
                buf = Buffer().write_varint(0).extend(buf)

        return Buffer().write_varint(len(buf)).extend(buf)

    def decode_packet(self, buf: Buffer, state: GameState, compression_threshold: int = -1) -> ServerBoundPacket:
        """Decodes and (if necessary) decompresses a ServerBoundPacket."""

        # decompress packet if necessary
        if compression_threshold >= 0:
            uncompressed_length = buf.read_varint()

            if uncompressed_length > 0:
                buf = Buffer(zlib.decompress(buf.read_bytes()))

        packet_id = buf.read_varint()

        # attempt to get packet class from given state and packet id
        try:
            packet_class = self.packets[state].server_bound[packet_id]
        except KeyError:
            raise UnknownPacketIdError(self.protocol, state, packet_id, PacketDirection.SERVERBOUND)
        
        return packet_class.unpack(buf)
    
