"""Contains packets related to commands"""

from __future__ import annotations

from typing import List

from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket

__all__ = ("PlayDeclareCommands",)


class PlayDeclareCommands(ClientBoundPacket):
    """Tells the clients what commands there are. (Server -> Client)

    :param List[dict] nodes: The command nodes, a list of dictionaries. The first item is assumed to be the root node.
    :attr int id: Unique packet ID.
    :attr nodes:
    """

    id = 0x12

    def __init__(
        self, nodes: List[dict]
    ) -> None:
        super().__init__()

        self.nodes = nodes

    def pack(self) -> Buffer:
        buf = Buffer().write_varint(len(self.nodes))
        
        for node in self.nodes:
            buf.write_node(node)
        
        return buf.write_varint(0)
