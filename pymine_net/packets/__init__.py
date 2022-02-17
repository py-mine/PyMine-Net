from typing import Dict, Union
import importlib

from pymine_net.types.packet_map import PacketMap, StatePacketMap
from pymine_net.enums import GameState

__all__ = ("load_packet_map",)

GAME_STATES = {
    GameState.HANDSHAKING: "handshaking",
    GameState.STATUS: "status",
    GameState.LOGIN: "login",
    GameState.PLAY: "play",
}


def load_packet_map(protocol: Union[int, str]) -> PacketMap:
    packets: Dict[GameState, StatePacketMap] = {}

    for state, state_name in GAME_STATES.items():
        module = importlib.import_module(f"pymine_net.packets.{protocol}.{state_name}")
        packets[state] = StatePacketMap.from_list(state, [getattr(module, c) for c in dir(module)])

    return PacketMap(protocol, packets)
