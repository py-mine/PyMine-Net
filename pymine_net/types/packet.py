from __future__ import annotations

from pymine_net.strict_abc import StrictABC, abstract, optionalabstract
from pymine_net.types.buffer import Buffer

__all__ = ("Packet", "ServerBoundPacket", "ClientBoundPacket")


class Packet(StrictABC):
    """Base Packet class.

    :param int id: Packet identification number. Defaults to None.
    :ivar id:
    """

    def __init__(self):
        self.id: int = self.__class__.id


class ServerBoundPacket(Packet):
    """Base Packet class for packets received from the client. (Client -> Server)

    :param int id: Packet identification number. Defaults to None.
    :ivar id:
    """

    @optionalabstract
    def pack(self) -> Buffer:
        raise NotImplementedError

    @abstract
    @classmethod
    def unpack(cls, buf: Buffer) -> ServerBoundPacket:
        pass


class ClientBoundPacket(Packet):
    """Base Packet class for packets to be sent from the server. (Server -> Client)

    :param int id: Packet identification number. Defaults to None.
    :ivar id:
    """

    @abstract
    def pack(self) -> Buffer:
        pass

    @classmethod
    @optionalabstract
    def unpack(cls, buf: Buffer) -> ServerBoundPacket:
        raise NotImplementedError
