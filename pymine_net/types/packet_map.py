from __future__ import annotations

from typing import Dict, Tuple, Union, List, Type

from pymine_net import Packet
from pymine_net.enums import GameState
from pymine_net.types.packet import ServerBoundPacket, ClientBoundPacket


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
    def from_list(cls, state: GameState, packets: List[Type[Packet]]) -> StatePacketMap:
        packets = [p for p in packets if isinstance(p, type)]

        return cls(
            state,
            {p.id: p for p in packets if issubclass(p, ServerBoundPacket)},
            {p.id: p for p in packets if issubclass(p, ClientBoundPacket)},
        )


class PacketMap:
    """Stores a Minecraft protocol's packets"""

    def __init__(self, protocol: Union[str, int], packets: Dict[GameState, StatePacketMap]):
        self.protocol = protocol
        self.packets = packets

    def get_server_bound(self, state: GameState, packet_id: int):
        """Gets a server bound packet by its GameState and packet id."""

        return self.packets[state].server_bound[packet_id]

    def get_client_bound(self, state: GameState, packet_id: int):
        """Gets a client bound packet by its GameState and packet id."""

        return self.packets[state].client_bound[packet_id]

    def __getitem__(self, key: Tuple[GameState, int]) -> Type[ServerBoundPacket]:
        """Shortcut for get_server_bound(...)"""

        return self.get_server_bound(*key)
