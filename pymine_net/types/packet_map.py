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
        serverbound: Dict[int, Type[ServerBoundPacket]],
        clientbound: Dict[int, Type[ClientBoundPacket]],
    ):
        self.state = state
        self.serverbound = serverbound
        self.clientbound = clientbound

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

    def __init__(
        self, protocol: Union[str, int], packets: Dict[GameState, StatePacketMap]
    ):
        self.protocol = protocol
        self.packets = packets

    def __getitem__(self, key: Tuple[GameState, int]) -> Type[ServerBoundPacket]:
        state: GameState
        packet_id: int

        (state, packet_id) = key

        return self.packets[state].serverbound[packet_id]
