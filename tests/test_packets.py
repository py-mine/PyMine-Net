import colorama
import pytest
import sys
import os

colorama.init(autoreset=True)

# fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymine_net.enums import GameState
from pymine_net import load_packet_map


@pytest.mark.parametrize( # GameState: (clientbound, serverbound)
    "protocol, config", (
        [757, {GameState.HANDSHAKING: (None, 0x0), GameState.STATUS: (0x1, 0x1), GameState.LOGIN: (0x4, 0x2), GameState.PLAY: (0x67, 0x2F)}],
    )
)
def test_ensure_all_packets(protocol, config):
    packet_map = load_packet_map(protocol)
    initial_check = True

    print(f"PACKET CHECK (protocol={protocol}): ", end="")

    for state in [GameState.HANDSHAKING, GameState.STATUS, GameState.LOGIN, GameState.PLAY]:
        missing_clientbound = []
        missing_serverbound = []

        c = config[state]
        
        # check if there are supposed to be clientbound packets
        if c[0] is not None:
            for i in range(0, c[0]):  # iterate through packet ids which should be there
                if i not in packet_map.packets[state].client_bound:
                    missing_clientbound.append(f"0x{i:02X}")

        # check if there are supposed to be serverbound packets
        if c[1] is not None:
            for i in range(0, c[1]):  # iterate through packet ids which should be there
                if i not in packet_map.packets[state].server_bound:
                    missing_serverbound.append(f"0x{i:02X}")
        
        if (missing_serverbound or missing_clientbound) and initial_check:
            initial_check = False
            print()

        if missing_clientbound:
            print(f"{colorama.Style.BRIGHT}{colorama.Fore.RED}MISSING (state={state.name}, CLIENT-BOUND):{colorama.Style.RESET_ALL}", ", ".join(missing_clientbound))

        if missing_serverbound:
            print(f"{colorama.Style.BRIGHT}{colorama.Fore.RED}MISSING (state={state.name}, SERVER-BOUND):{colorama.Style.RESET_ALL}", ", ".join(missing_serverbound))

    if initial_check:
        print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}All packets present!")
