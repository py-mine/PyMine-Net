from typing import Dict, Union
import importlib

from pymine_net import PacketMap, StatePacketMap
from pymine_net.enums import GameState

GAME_STATES = {
    GameState.HANDSHAKING: "handshaking",
    GameState.STATUS: "status",
    GameState.LOGIN: "login",
    GameState.PLAY: "play",
}


def load_packet_map(protocol: Union[int, str]) -> PacketMap:
    packets: Dict[GameState, StatePacketMap]

    for state, state_name in GAME_STATES.items():
        module = importlib.import_module(f".packets.{protocol}.{state_name}")
        packets[state] = StatePacketMap.from_list(state, [getattr(module, c) for c in module.__all__])

    return PacketMap(protocol, packets)
