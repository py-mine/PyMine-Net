from __future__ import annotations

from typing import Dict, List, Literal, Tuple, Type, Union, TYPE_CHECKING, overload

from pymine_net.enums import GameState, PacketDirection
from pymine_net.errors import DuplicatePacketIdError
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

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
        packets: List[Union[Type[ServerBoundPacket], Type[ClientBoundPacket]]],
        *,
        check_duplicates: bool = False,
    ) -> Self:
        server_bound = {}
        client_bound = {}
        for packet in packets:
            if issubclass(packet, ServerBoundPacket):
                if check_duplicates and packet.id in server_bound:
                    raise DuplicatePacketIdError("unknown", state, packet.id, PacketDirection.SERVERBOUND)
                server_bound[packet.id] = packet
            elif issubclass(packet, ClientBoundPacket):
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

    @overload
    def __getitem__(self, __key: Tuple[Literal[PacketDirection.CLIENTBOUND], int, int]) -> ClientBoundPacket:
        ...

    @overload
    def __getitem__(self, __key: Tuple[Literal[PacketDirection.SERVERBOUND], int, int]) -> ServerBoundPacket:
        ...

    def __getitem__(self, __key: Tuple[PacketDirection, int, int]) -> Union[ClientBoundPacket, ServerBoundPacket]:
        direction, state, packet_id = __key

        if direction is PacketDirection.CLIENTBOUND:
            return self.packets[state].client_bound[packet_id]

        return self.packets[state].server_bound[packet_id]
