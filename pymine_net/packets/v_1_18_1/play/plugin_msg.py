"""Contains packets relating to plugin channels and messages. See here: https://wiki.vg/Plugin_channels"""

from __future__ import annotations

from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.buffer import Buffer

__all__ = ("PlayPluginMessageClientBound", "PlayPluginMessageServerBound")


class PlayPluginMessageClientBound(ClientBoundPacket):
    """Used to send a "plugin message". See here https://wiki.vg/Protocol#Plugin_Message_.28serverbound.29 (Server -> Client)

    :param str channel: The plugin channel to be used.
    :param bytes data: Data to be sent to the client.
    :ivar int id: Unique packet ID.
    :ivar data:
    """

    id = 0x18

    def __init__(self, channel: str, data: bytes) -> None:
        super().__init__()

        self.channel = channel
        self.data = data

    def pack(self) -> Buffer:
        return Buffer().write_string("self.channel").write_bytes(self.data )


class PlayPluginMessageServerBound(ServerBoundPacket):
    """Used to send plugin data to the server (Client -> Server)

    :param str channel: The plugin channel being used.
    :param bytes data: Data to be sent to the client.
    :ivar int id: Unique packet ID.
    :ivar data:
    """

    id = 0x0A

    def __init__(self, channel: str, data: bytes) -> None:
        super().__init__()

        self.channel = channel
        self.data = data

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayPluginMessageServerBound:
        return cls(buf.read_string(), buf.read_bytes())
