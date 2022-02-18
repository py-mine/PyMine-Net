from typing import Dict, Union
import importlib
import warnings
import os

from pymine_net.types.packet_map import PacketMap, StatePacketMap
from pymine_net.types.packet import Packet
from pymine_net.enums import GameState

__all__ = ("load_packet_map",)

GAME_STATES = {
    GameState.HANDSHAKING: "handshaking",
    GameState.STATUS: "status",
    GameState.LOGIN: "login",
    GameState.PLAY: "play",
}

# the directory this file is contained in
FILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_packet_map(protocol: Union[int, str]) -> PacketMap:
    packets: Dict[GameState, StatePacketMap] = {}

    for state, state_name in GAME_STATES.items():
        module_base = ["packets", str(protocol), state_name]

        for file_name in os.listdir(os.path.join(FILE_DIR, *module_base)):
            if not file_name.endswith(".py"):
                continue

            module = importlib.import_module(".".join(["pymine_net", *module_base, file_name[:-3]]))

            if not hasattr(module, "__all__"):
                warnings.warn(f"{module.__name__} is missing attribute __all__ and cannot be loaded.")
                continue
            
            packet_classes = []

            for member_name in module.__all__:
                try:
                    obj = getattr(module, member_name)
                except AttributeError:
                    warnings.warn(f"{module.__name__} is missing member {member_name!r} present in __all__.")
                else:
                    if issubclass(obj, Packet):
                        packet_classes.append(obj)

            packets[state] = StatePacketMap.from_list(state, packet_classes)

    return PacketMap(protocol, packets)
