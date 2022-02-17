from __future__ import annotations

from abc import ABC, abstractmethod, abstractclassmethod

from pymine_net import Buffer

__all__ = ("Packet", "ClientPacket", "ServerPacket")


class Packet(ABC):
    """Base Packet class.

    :param int id: Packet identifaction number. Defaults to None.
    :ivar id:
    """

    def __init__(self):
        self.id: int = self.__class__.id


class ClientPacket(Packet):
    """Base Packet class for packets received from the client. (Client -> Server)

    :param int id: Packet identifaction number. Defaults to None.
    :ivar id:
    """

    @abstractclassmethod
    def unpack(cls, buf: Buffer) -> ClientPacket:
        pass


class ServerPacket(Packet):
    """Base Packet class for packets to be sent from the server. (Server -> Client)

    :param int id: Packet identifaction number. Defaults to None.
    :ivar id:
    """

    @abstractmethod
    def pack(self) -> Buffer:
        pass
