from __future__ import annotations

from abc import ABC, abstractmethod, abstractclassmethod

from pymine_net.types.buffer import Buffer

__all__ = ("Packet", "ServerBoundPacket", "ClientBoundPacket")


class Packet(ABC):
    """Base Packet class.

    :param int id: Packet identifaction number. Defaults to None.
    :ivar id:
    """

    def __init__(self):
        self.id: int = self.__class__.id


class ServerBoundPacket(Packet):
    """Base Packet class for packets received from the client. (Client -> Server)

    :param int id: Packet identifaction number. Defaults to None.
    :ivar id:
    """

    @abstractclassmethod
    def unpack(cls, buf: Buffer) -> ServerBoundPacket:
        pass


class ClientBoundPacket(Packet):
    """Base Packet class for packets to be sent from the server. (Server -> Client)

    :param int id: Packet identifaction number. Defaults to None.
    :ivar id:
    """

    @abstractmethod
    def pack(self) -> Buffer:
        pass
