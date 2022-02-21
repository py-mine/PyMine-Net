import os
import sys
import uuid
from typing import Dict, Optional, Tuple, Union

import colorama
from pymine_net.strict_abc import is_abstract
from pymine_net.types.packet import ServerBoundPacket
import pytest

from pymine_net.types.buffer import Buffer
from pymine_net.types.chat import Chat

colorama.init(autoreset=True)

# fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymine_net import load_packet_map
from pymine_net.enums import GameState

STATE_LIST = [GameState.HANDSHAKING, GameState.STATUS, GameState.LOGIN, GameState.PLAY]
CHECKABLE_ANNOS = {bool, int, float, bytes, str, uuid.UUID, Chat}
CHECKABLE_ANNOS.update({a.__name__ for a in CHECKABLE_ANNOS})


@pytest.mark.parametrize(  # GameState: (clientbound, serverbound)
    "protocol, config",
    (
        [
            757,
            {
                GameState.HANDSHAKING: (None, 0x0),
                GameState.STATUS: (0x1, 0x1),
                GameState.LOGIN: (0x4, 0x2),
                GameState.PLAY: (0x67, 0x2F),
            },
        ],
    ),
)
def test_ensure_all_packets(
    capsys, protocol: Union[int, str], config: Dict[GameState, Tuple[Optional[int], Optional[int]]]
):
    packet_map = load_packet_map(protocol, debug=True)
    initial_check = True

    print(f"PACKET CHECK (protocol={protocol}): ", end="")

    for state in STATE_LIST:
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
            print(
                f"{colorama.Style.BRIGHT}{colorama.Fore.RED}MISSING (state={state.name}, CLIENT-BOUND):{colorama.Style.RESET_ALL}",
                ", ".join(missing_clientbound),
            )

        if missing_serverbound:
            print(
                f"{colorama.Style.BRIGHT}{colorama.Fore.RED}MISSING (state={state.name}, SERVER-BOUND):{colorama.Style.RESET_ALL}",
                ", ".join(missing_serverbound),
            )

    if initial_check:
        print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}All packets present!")
    else:
        reason = "Missing packets\n" + capsys.readouterr().out
        pytest.xfail(reason=reason)


@pytest.mark.parametrize("protocol", (757,))
def test_pack_clientbound_packets(protocol: Union[int, str]):
    packet_map = load_packet_map(protocol)

    # iterate through each packet class in the state list
    for state in STATE_LIST:
        packet_classes = {**packet_map.packets[state].client_bound, **packet_map.packets[state].server_bound}.values()
        
        for packet_class in packet_classes:
            # since ServerBoundPacket.pack(...) is an optional abstract method we have to
            # check if a ServerBoundPacket's pack() method is actually implemented or not
            if issubclass(packet_class, ServerBoundPacket):
                if is_abstract(packet_class.pack):
                    continue

            annos = packet_class.__init__.__annotations__.copy()

            # get rid of return annotation if there is one
            annos.pop("return", None)

            kwargs = {}

            for anno_name, anno_type in annos.items():
                if anno_type is bool or anno_type == "bool":
                    kwargs[anno_name] = True
                elif anno_type is int or anno_type == "int":
                    kwargs[anno_name] = 1
                elif anno_type is float or anno_type == "float":
                    kwargs[anno_name] = 123.123
                elif anno_type is bytes or anno_type == "bytes":
                    kwargs[anno_name] = b"abc\x01\x02\x03"
                elif anno_type is str or anno_type == "str":
                    kwargs[anno_name] = "test string123 !@#$%^&*()-_=+"
                elif anno_type is uuid.UUID or anno_type == "UUID":
                    kwargs[anno_name] = uuid.uuid4()
                elif anno_type is Chat or anno_type == "Chat":
                    kwargs[anno_name] = Chat("test chat message 123")

            # not all args could have dummy values generated, so we can't test this packet
            if len(kwargs) != len(annos):
                continue

            packet = packet_class(**kwargs)  # create instance of packet from dummy data
            buffer = packet.pack()  # pack packet into a Buffer

            assert isinstance(buffer, Buffer)

            # some clientbound packets have a corresponding unpack method, so we can try to test that
            try:
                decoded_packet = packet_class.unpack(buffer)

                assert isinstance(decoded_packet, packet_class)
                assert decoded_packet.__dict__ == packet.__dict__
            except NotImplementedError:
                pass

            # some packets don't take any arguments and the data sent is just the packet id
            if len(kwargs) > 0:
                assert len(buffer) >= 1
