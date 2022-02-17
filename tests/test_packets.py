from pymine_net.types.packet import ServerBoundPacket
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymine_net.enums import GameState
from pymine_net import load_packet_map


@pytest.mark.parametrize("protocol", ([757], ["757"]))
def test_loading_packets(protocol):
    packet_map = load_packet_map(757)
    
    assert issubclass(packet_map[GameState.HANDSHAKING, 0], ServerBoundPacket)
    assert issubclass(packet_map[GameState.STATUS, 0], ServerBoundPacket)
    assert issubclass(packet_map[GameState.LOGIN, 0], ServerBoundPacket)
    assert issubclass(packet_map[GameState.PLAY, 0], ServerBoundPacket)
