from __future__ import annotations

from typing import Dict, Tuple, Union, List, Type

from pymine_net import Packet
from pymine_net.enums import GameState
from pymine_net.types.packet import ServerBoundPacket, ClientBoundPacket


class DuplicatePacketIdError(Exception):
    def __init__(self, protocol: Union[str, int], state: GameState, packet_id: int, direction: str):
        super().__init__(f"Duplicate packet ID found (protocol={protocol}, state={state.name}, {direction}): 0x{packet_id:02X}")

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
    def from_list(cls, state: GameState, packets: List[Type[Packet]], *, check_duplicates: bool = False) -> StatePacketMap:
        self = cls(
            state,
            {p.id: p for p in packets if issubclass(p, ServerBoundPacket)},
            {p.id: p for p in packets if issubclass(p, ClientBoundPacket)},
        )

        if check_duplicates:
            for packet_id in self.server_bound.keys():
                found = [p for p in packets if p.id == packet_id and issubclass(p, ServerBoundPacket)]

                if len(found) > 1:
                    raise DuplicatePacketIdError("unknown", state, packet_id, "SERVER-BOUND")

            for packet_id in self.client_bound.keys():
                found = [p for p in packets if p.id == packet_id and issubclass(p, ClientBoundPacket)]

                if len(found) > 1:
                    raise DuplicatePacketIdError("unknown", state, packet_id, "CLIENT-BOUND")
        
        return self


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
