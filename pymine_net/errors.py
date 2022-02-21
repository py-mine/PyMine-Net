from typing import Union

from pymine_net.enums import GameState, PacketDirection


class PyMineNetError(Exception):
    pass


class UnknownPacketIdError(Exception):
    def __init__(self, protocol: Union[str, int], state: GameState, packet_id: int, direction: PacketDirection):
        super().__init__(f"Unknown packet ID 0x{packet_id:02X} (protocol={protocol}, state={state.name}, {direction.value})")

        self.protocol = protocol
        self.state = state
        self.packet_id = packet_id
        self.direction = direction


class DuplicatePacketIdError(Exception):
    def __init__(self, protocol: Union[str, int], state: GameState, packet_id: int, direction: PacketDirection):
        super().__init__(
            f"Duplicate packet ID found (protocol={protocol}, state={state.name}, {direction}): 0x{packet_id:02X}"
        )

        self.protocol = protocol
        self.state = state
        self.packet_id = packet_id
        self.direction = direction
