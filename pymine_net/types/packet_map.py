from __future__ import annotations

import zlib
from typing import Dict, List, Tuple, Type, Union

from pymine_net.enums import GameState, PacketDirection
from pymine_net.errors import DuplicatePacketIdError, UnknownPacketIdError
from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, Packet, ServerBoundPacket


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
                    raise DuplicatePacketIdError(
                        "unknown", state, packet_id, PacketDirection.SERVERBOUND
                    )

            for packet_id in self.client_bound.keys():
                found = [
                    p for p in packets if p.id == packet_id and issubclass(p, ClientBoundPacket)
                ]

                if len(found) > 1:
                    raise DuplicatePacketIdError(
                        "unknown", state, packet_id, PacketDirection.CLIENTBOUND
                    )

        return self


class PacketMap:
    """Stores a Minecraft protocol's packets"""

    def __init__(self, protocol: Union[str, int], packets: Dict[GameState, StatePacketMap]):
        self.protocol = protocol
        self.packets = packets

    def __getitem__(self, key: Tuple[PacketDirection, int, int]) -> Packet:
        direction, state, packet_id = key

        if direction == PacketDirection.CLIENTBOUND:
            return self.packets[state].client_bound[packet_id]

        return self.packets[state].server_bound[packet_id]
