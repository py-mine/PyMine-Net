from __future__ import annotations

from typing import Dict, List, Tuple, Type, Union, TYPE_CHECKING

from pymine_net.enums import GameState, PacketDirection
from pymine_net.errors import DuplicatePacketIdError
from pymine_net.types.packet import ClientBoundPacket, Packet, ServerBoundPacket

if TYPE_CHECKING:
    from typing_extensions import Self


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
        cls,
        state: GameState,
        packets: List[Union[ServerBoundPacket, ClientBoundPacket]],
        *,
        check_duplicates: bool = False,
    ) -> Self:
        server_bound = {}
        client_bound = {}
        for packet in packets:
            if isinstance(packet, ServerBoundPacket):
                if check_duplicates and packet.id in server_bound:
                    raise DuplicatePacketIdError("unknown", state, packet.id, PacketDirection.SERVERBOUND)
                server_bound[packet.id] = packet
            elif isinstance(packet, ClientBoundPacket):
                if check_duplicates and packet.id in client_bound:
                    raise DuplicatePacketIdError("unknown", state, packet.id, PacketDirection.CLIENTBOUND)
                client_bound[packet.id] = packet
            else:
                raise TypeError(f"Expected ServerBoundPacket or ClientBoundPacket, got {type(packet)}")

        return cls(state, server_bound, client_bound)


class PacketMap:
    """Stores a Minecraft protocol's packets"""

    def __init__(self, protocol: Union[str, int], packets: Dict[GameState, StatePacketMap]):
        self.protocol = protocol
        self.packets = packets

    def __getitem__(self, __key: Tuple[PacketDirection, int, int]) -> Packet:
        direction, state, packet_id = __key

        if direction is PacketDirection.CLIENTBOUND:
            return self.packets[state].client_bound[packet_id]

        return self.packets[state].server_bound[packet_id]
