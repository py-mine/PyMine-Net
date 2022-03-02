import importlib
from pathlib import Path
import warnings
from typing import Dict, List, Union

from pymine_net.enums import GameState
from pymine_net.types.packet import Packet
from pymine_net.types.packet_map import DuplicatePacketIdError, PacketMap, StatePacketMap

__all__ = ("load_packet_map",)


GAME_STATES = [(name.lower(), state) for name, state in GameState.__members__.items()]

# the directory this file is contained in
FILE_DIR = Path(__file__).parent.absolute()

PROTOCOL_MAP = {757: "v_1_18_1"}


def load_packet_map(protocol: Union[int, str], *, debug: bool = False) -> PacketMap:
    """
    Iterates through the protocol's packets direction and constructs a PacketMap.
    - Used for automatic decoding of incoming packet ids into packet classes for decoding the entire packet.
    - Also necessary for the packet tests to function.
    """

    protocol = PROTOCOL_MAP.get(protocol, protocol)
    packets: Dict[GameState, StatePacketMap] = {}

    for state_name, state in GAME_STATES:
        module_base = [str(protocol), state_name]

        packet_classes: List[Packet] = []

        # iterate through the files in the <state> folder
        for path in Path(FILE_DIR, *module_base).iterdir():
            if not path.is_file() or not path.name.endswith(".py"):
                continue

            # import the file (pymine_net.packets.<protocol>.<state>.<packet group>)
            module = importlib.import_module(".".join(["pymine_net", "packets", *module_base, path.name[:-3]]))

            if debug and not hasattr(module, "__all__"):
                warnings.warn(f"{module.__name__} is missing member __all__ and cannot be loaded.")
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
            packets[state] = StatePacketMap.from_list(state, packet_classes, check_duplicates=debug)
        except DuplicatePacketIdError as e:  # re-raise with protocol included in exception
            raise DuplicatePacketIdError(protocol, e.state, e.packet_id, e.direction)

    return PacketMap(protocol, packets)
