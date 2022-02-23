import asyncio

import pytest

from pymine_net.enums import GameState
from pymine_net.net.asyncio import (
    AsyncProtocolClient,
    AsyncProtocolServer,
    AsyncProtocolServerClient,
)
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


# proactor event loop vomits an error on exit on windows due to a Python bug
@pytest.fixture
def event_loop():
    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    yield asyncio.get_event_loop()


@pytest.mark.asyncio
async def test_asyncio_net_status():
    class TestAsyncTCPServer(AsyncProtocolServer):
        async def new_client_connected(self, client: AsyncProtocolServerClient) -> None:
            packet = await client.read_packet()
            assert isinstance(packet, HandshakeHandshake)
            assert packet.protocol == TESTING_PROTOCOL
            assert packet.address == "localhost"
            assert packet.port == TESTING_PORT
            assert packet.next_state == GameState.STATUS

            client.state = packet.next_state

            packet = await client.read_packet()
            assert isinstance(packet, StatusStatusRequest)

            await client.write_packet(StatusStatusResponse(TESTING_STATUS_JSON))

            packet = await client.read_packet()
            assert isinstance(packet, StatusStatusPingPong)
            assert packet.payload == TESTING_RANDOM_LONG
            await client.write_packet(packet)

    packet_map = load_packet_map(TESTING_PROTOCOL)

    server = TestAsyncTCPServer(TESTING_HOST, TESTING_PORT, TESTING_PROTOCOL, packet_map)
    server_task = asyncio.create_task(server.run())

    client = AsyncProtocolClient(TESTING_HOST, TESTING_PORT, TESTING_PROTOCOL, packet_map)
    await client.connect()

    await client.write_packet(
        HandshakeHandshake(TESTING_PROTOCOL, TESTING_HOST, TESTING_PORT, GameState.STATUS)
    )
    client.state = GameState.STATUS

    await client.write_packet(StatusStatusRequest())

    packet = await client.read_packet()
    assert isinstance(packet, StatusStatusResponse)
    assert packet.data == TESTING_STATUS_JSON

    await client.write_packet(StatusStatusPingPong(TESTING_RANDOM_LONG))
    packet = await client.read_packet()
    assert isinstance(packet, StatusStatusPingPong)
    assert packet.payload == TESTING_RANDOM_LONG

    await client.close()

    server_task.cancel()
    await server.close()
