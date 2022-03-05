import pkgutil
import warnings
from pathlib import Path
from typing import Dict, Iterator, NoReturn, Type, Union

from pymine_net.enums import GameState
from pymine_net.types.packet import Packet
from pymine_net.types.packet_map import DuplicatePacketIdError, PacketMap, StatePacketMap

__all__ = ("load_packet_map",)


# the directory this file is contained in
FILE_DIR = Path(__file__).parent

PROTOCOL_MAP = {757: "v_1_18_1"}


def walk_packet_classes(
    protocol_name: str, state: GameState, debug: bool = False
) -> Iterator[Type[Packet]]:
    """
    Try to import every pymine.packets.{protocol_name}.{state.name} package,
    and search it's __all__ for presence of subclasses of the Packet class.
    When a subclass is found, yield it.
    """
    # Directories in the package under protocol_name should always contain
    # all of the GameState's enum names, as subpackages. So we can assume
    # that this path exists, and if not, it will result in an ImportError
    # later.
    path = str(Path(FILE_DIR, protocol_name, state.name).absolute())
    prefix = f"pymine_net.packets.{protocol_name}.{state.name}"

    def on_error(name: str) -> NoReturn:
        raise ImportError(name=name)

    for module in pkgutil.walk_packages(path, prefix, onerror=on_error):
        if debug and not hasattr(module, "__all__"):
            warnings.warn(f"{module.__name__} is missing member __all__ and cannot be loaded.")
            continue

        for member_name in module.__all__:
            try:
                obj = getattr(module, member_name)
            except AttributeError:
                if debug:
                    warnings.warn(
                        f"{module.__name__} is missing member {member_name!r} present in __all__."
                    )
            else:
                if issubclass(obj, Packet):
                    yield obj


def load_packet_map(protocol: Union[int, str], *, debug: bool = False) -> PacketMap:
    """
    Collects all packet classes for each GameState for given protocol to construct a PacketMap.

    - If passed protocol is an `int`, we treat it as a version number and use the corresponding
    protocol import name defined in PROTOCOL_MAP.
    - If it's a `str`, we treat it as the import name directly.

    This is useful for automatic decoding of incoming packet ids into packet classes for decoding
    the entire packet.
    """

    if isinstance(protocol, int):
        # If given protocol was int (version) and it isn't present in
        # the protocol map, we end with ha KeyError since we don't know
        # what to import.
        protocol = PROTOCOL_MAP[protocol]

    packets: Dict[GameState, StatePacketMap] = {}

    for state in GameState:
        packet_classes = [
            packet_class for packet_class in walk_packet_classes(protocol, state, debug)
        ]

        # attempt to create the StatePacketMap from the list of loaded packets.
        try:
            packets[state] = StatePacketMap.from_list(state, packet_classes, check_duplicates=debug)
        except DuplicatePacketIdError as exc:  # re-raise with protocol included in exception
            raise DuplicatePacketIdError(protocol, exc.state, exc.packet_id, exc.direction)

    return PacketMap(protocol, packets)
