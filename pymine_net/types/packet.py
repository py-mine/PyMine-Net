from __future__ import annotations

from abc import abstractmethod
from typing import ClassVar, Optional

from pymine_net.strict_abc import StrictABC, optionalabstractmethod
from pymine_net.types.buffer import Buffer

__all__ = ("Packet", "ServerBoundPacket", "ClientBoundPacket")


class Packet(StrictABC):
    """Base Packet class.

    :cvar id: Packet identification number. Defaults to None.
    """

    id: ClassVar[Optional[int]] = None


class ServerBoundPacket(Packet):
    """Base Packet class for packets received from the client. (Client -> Server)

    :cvar id: Packet identification number. Defaults to None.
    """

    @optionalabstractmethod
    def pack(self) -> Buffer:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def unpack(cls, buf: Buffer) -> ServerBoundPacket:
        pass


class ClientBoundPacket(Packet):
    """Base Packet class for packets to be sent from the server. (Server -> Client)

    :cvar id: Packet identification number. Defaults to None.
    """

    @abstractmethod
    def pack(self) -> Buffer:
        pass

    @classmethod
    @optionalabstractmethod
    def unpack(cls, buf: Buffer) -> ClientBoundPacket:
        raise NotImplementedError
