import importlib
import os
import warnings
from typing import Dict, List, Union

from pymine_net.enums import GameState
from pymine_net.types.packet import Packet
from pymine_net.types.packet_map import DuplicatePacketIdError, PacketMap, StatePacketMap

__all__ = ("load_packet_map",)

GAME_STATES = {
    GameState.HANDSHAKING: "handshaking",
    GameState.STATUS: "status",
    GameState.LOGIN: "login",
    GameState.PLAY: "play",
}

# the directory this file is contained in
FILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_packet_map(protocol: Union[int, str], *, debug: bool = False) -> PacketMap:
    packets: Dict[GameState, StatePacketMap] = {}

    for state, state_name in GAME_STATES.items():
        module_base = ["packets", str(protocol), state_name]
        
        packet_classes: List[Packet] = []

        # iterate through the files in the <state> folder
        for file_name in os.listdir(os.path.join(FILE_DIR, *module_base)):
            if not file_name.endswith(".py"):
                continue

            # import the file (pymine_net.packets.<protocol>.<state>.<packet group>)
            module = importlib.import_module(".".join(["pymine_net", *module_base, file_name[:-3]]))

            if debug and not hasattr(module, "__all__"):
                warnings.warn(
                    f"{module.__name__} is missing member __all__ and cannot be loaded."
                )
                continue

            # iterate through object names in module.__all__
            for member_name in module.__all__:
                # attempt to get object, warn if it's not actually present
                try:
                    obj = getattr(module, member_name)
                except AttributeError:
                    if debug:
                        warnings.warn(
                            f"{module.__name__} is missing member {member_name!r} present in __all__."
                        )
                else:
                    if issubclass(obj, Packet):
                        packet_classes.append(obj)

        # attempt to create the StatePacketMap from the list of loaded packets.
        try:
            packets[state] = StatePacketMap.from_list(
                state, packet_classes, check_duplicates=debug
            )
        except DuplicatePacketIdError as e:  # re-raise with protocol included in exception
            raise DuplicatePacketIdError(protocol, e.state, e.packet_id, e.direction)

    return PacketMap(protocol, packets)
