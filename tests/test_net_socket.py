from concurrent.futures import ThreadPoolExecutor

from pymine_net.enums import GameState
from pymine_net.net.socket import SocketProtocolServer, SocketProtocolServerClient, SocketTCPClient
from pymine_net.packets import load_packet_map
from pymine_net.packets.v_1_18_1.handshaking.handshake import HandshakeHandshake
from pymine_net.packets.v_1_18_1.status.status import (
    StatusStatusPingPong,
    StatusStatusRequest,
    StatusStatusResponse,
)

TESTING_PROTOCOL = 757
TESTING_HOST = "localhost"
TESTING_PORT = 12345
TESTING_RANDOM_LONG = 1234567890
TESTING_STATUS_JSON = {
    "version": {"name": "1.18.1", "protocol": TESTING_PROTOCOL},
    "players": {
        "max": 20,
        "online": 0,
        "sample": [{"name": "Iapetus11", "id": "cbcfa252-867d-4bda-a214-776c881cf370"}],
    },
    "description": {"text": "Hello world"},
    "favicon": None,
}


def test_socket_net_status():
    class TestSocketTCPServer(SocketProtocolServer):
        def new_client_connected(self, client: SocketProtocolServerClient) -> None:
            packet = client.read_packet()
            assert isinstance(packet, HandshakeHandshake)
            assert packet.protocol == TESTING_PROTOCOL
            assert packet.address == "localhost"
            assert packet.port == TESTING_PORT
            assert packet.next_state == GameState.STATUS

            client.state = packet.next_state

            packet = client.read_packet()
            assert isinstance(packet, StatusStatusRequest)

            client.write_packet(StatusStatusResponse(TESTING_STATUS_JSON))

            packet = client.read_packet()
            assert isinstance(packet, StatusStatusPingPong)
            assert packet.payload == TESTING_RANDOM_LONG
            client.write_packet(packet)

    packet_map = load_packet_map(TESTING_PROTOCOL)

    server = TestSocketTCPServer(TESTING_HOST, TESTING_PORT, TESTING_PROTOCOL, packet_map)
    threadpool = ThreadPoolExecutor()
    threadpool.submit(server.run)

    client = SocketTCPClient(TESTING_HOST, TESTING_PORT, TESTING_PROTOCOL, packet_map)
    client.connect()

    client.write_packet(
        HandshakeHandshake(TESTING_PROTOCOL, TESTING_HOST, TESTING_PORT, GameState.STATUS)
    )
    client.state = GameState.STATUS

    client.write_packet(StatusStatusRequest())

    packet = client.read_packet()
    assert isinstance(packet, StatusStatusResponse)
    assert packet.data == TESTING_STATUS_JSON

    client.write_packet(StatusStatusPingPong(TESTING_RANDOM_LONG))
    packet = client.read_packet()
    assert isinstance(packet, StatusStatusPingPong)
    assert packet.payload == TESTING_RANDOM_LONG

    client.close()

    threadpool.shutdown(wait=False, cancel_futures=True)
    server.close()
