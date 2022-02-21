"""Contains packets related to entities."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union

import pymine_net.types.nbt as nbt
from pymine_net.types.buffer import Buffer
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = (
    "PlayBlockEntityData",
    "PlayQueryEntityNBT",
    "PlayInteractEntity",
    "PlayEntityStatus",
    "PlayEntityAction",
    "PlayEntityPosition",
    "PlayEntityPositionAndRotation",
    "PlayEntityRotation",
    "PlayRemoveEntityEffect",
    "PlayEntityHeadLook",
    "PlayAttachEntity",
    "PlayEntityVelocity",
    "PlayEntityTeleport",
    "PlayDestroyEntities",
    "PlayEntityMetadata",
    "PlayEntityEquipment",
)


class PlayBlockEntityData(ClientBoundPacket):
    """Sets the block entity associated with the block at the given location. (Server -> Client).

    :param int x: The x coordinate of the position.
    :param int y: The y coordinate of the position.
    :param int z: The z coordinate of the position.
    :param int action: The action to be carried out (see https://wiki.vg/Protocol#Block_Entity_Data).
    :param nbt.TAG nbt_data: The nbt data associated with the action/block.
    :ivar int id: Unique packet ID.
    :ivar x:
    :ivar y:
    :ivar z:
    :ivar action:
    :ivar nbt_data:
    """

    id = 0x0A

    def __init__(self, x: int, y: int, z: int, action: int, nbt_data: nbt.TAG):
        super().__init__()

        self.x = x
        self.y = y
        self.z = z
        self.action = action
        self.nbt_data = nbt_data

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_position(self.x, self.y, self.z)
            .write("B", self.action)
            .write_nbt(self.nbt_data)
        )


class PlayQueryEntityNBT(ServerBoundPacket):
    """Sent by the client when Shift+F3+I is used. (Client -> Server)

    :param int transaction_id: Incremental ID used so the client can verify responses.
    :param int entity_id: The ID of the entity to query.
    :ivar int id: Unique packet ID.
    :ivar transaction_id:
    :ivar entity_id:
    """

    id = 0x0C

    def __init__(self, transaction_id: int, entity_id: int):
        super().__init__()

        self.transaction_id = transaction_id
        self.entity_id = entity_id

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayQueryEntityNBT:
        return cls(buf.read_varint(), buf.read_varint())


class PlayInteractEntity(ServerBoundPacket):
    """Sent when a client clicks another entity, see here: https://wiki.vg/Protocol#Interact_Entity. (Client -> Server)

    :param int entity_id: The ID of the entity interacted with.
    :param int type_: Either interact (0), attack (1), or interact at (2).
    :param Optional[int] target_x: The x coordinate of where the target is, can be None.
    :param Optional[int] target_y: The y coordinate of where the target is, can be None.
    :param Optional[int] target_z: The z coordinate of where the target is, can be None.
    :param Optional[int] hand: The hand used.
    :param bool sneaking: Whether the client was sneaking or not.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar type_:
    :ivar target_x:
    :ivar target_y:
    :ivar target_z:
    :ivar hand:
    :ivar sneaking:
    """

    id = 0x0D

    def __init__(
        self,
        entity_id: int,
        type_: int,
        target_x: Optional[int],
        target_y: Optional[int],
        target_z: Optional[int],
        hand: Optional[int],
        sneaking: bool,
    ):
        super().__init__()

        self.entity_id = entity_id
        self.type_ = type_
        self.target_x = target_x
        self.target_y = target_y
        self.target_z = target_z
        self.hand = hand
        self.sneaking = sneaking

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayInteractEntity:
        return cls(
            buf.read_varint(),
            buf.read_varint(),
            buf.read_optional(buf.read_varint),
            buf.read_optional(buf.read_varint),
            buf.read_optional(buf.read_varint),
            buf.read_optional(buf.read_varint),
            buf.read("?"),
        )


class PlayEntityStatus(ClientBoundPacket):
    """Usually used to trigger an animation for an entity. (Server -> Client)

    :param int entity_id: The ID of the entity the status is for.
    :param int entity_status: Depends on the type of entity, see here: https://wiki.vg/Protocol#Entity_Status.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar entity_status:
    """

    id = 0x1B

    def __init__(self, entity_id: int, entity_status: int):
        super().__init__()

        self.entity_id = entity_id
        self.entity_status = entity_status

    def pack(self) -> Buffer:
        return Buffer().write("i", self.entity_id).write("b", self.entity_status)


class PlayEntityAction(ServerBoundPacket):
    """Sent by the client to indicate it has performed a certain action. (Client -> Server)

    :param int entity_id: The ID of the entity.
    :param int action_id: The action occurring, see here: https://wiki.vg/Protocol#Entity_Action.
    :param int jump_boost: Used with jumping while riding a horse.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar action_id:
    :ivar jump_boost:
    """

    id = 0x1B

    def __init__(self, entity_id: int, action_id: int, jump_boost: int):
        super().__init__()

        self.entity_id = entity_id
        self.action_id = action_id
        self.jump_boost = jump_boost

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayEntityAction:
        return cls(buf.read_varint(), buf.read_varint(), buf.read_varint())


class PlayEntityPosition(ClientBoundPacket):
    """Sent by the server when an entity moves less than 8 blocks. (Server -> Client)

    :param int entity_id: The Id of the entity moving.
    :param int dx: Delta (change in) x, -8 <-> 8.
    :param int dy: Delta (change in) y, -8 <-> 8.
    :param int dz: Delta (change in) z, -8 <-> 8.
    :param bool on_ground: Whether entity is on ground or not.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar dx:
    :ivar dy:
    :ivar dz:
    :ivar on_ground:
    """

    id = 0x29

    def __init__(self, entity_id: int, dx: int, dy: int, dz: int, on_ground: bool):
        super().__init__()

        self.entity_id = entity_id
        self.dx, self.dy, self.dz = dx, dy, dz
        self.on_ground = on_ground

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_varint(self.entity_id)
            .write("h", self.dx)
            .write("h", self.dy)
            .write("h", self.dz)
            .write("?", self.on_ground)
        )


class PlayEntityPositionAndRotation(ClientBoundPacket):
    """Sent by the server when an entity rotates and moves. (Server -> Client)

    :param int entity_id: The ID of the entity moving/rotationing.
    :param int dx: Delta (change in) x, -8 <-> 8.
    :param int dy: Delta (change in) y, -8 <-> 8.
    :param int dz: Delta (change in) z, -8 <-> 8.
    :param int yaw: The new yaw angle, the value being x/256 of a full rotation.
    :param int pitch: The new pitch angle, the value being x/256 of a full rotation.
    :param bool on_ground: Whether entity is on ground or not.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar dx:
    :ivar dy:
    :ivar dz:
    :ivar yaw:
    :ivar pitch:
    :ivar on_ground:
    """

    id = 0x2A

    def __init__(
        self, entity_id: int, dx: int, dy: int, dz: int, yaw: int, pitch: int, on_ground: bool
    ):
        super().__init__()

        self.entity_id = entity_id
        self.dx, self.dy, self.dz = dx, dy, dz
        self.yaw = yaw
        self.pitch = pitch
        self.on_ground = on_ground

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_varint(self.entity_id)
            .write("h", self.dx)
            .write("h", self.dy)
            .write("h", self.dz)
            .write_byte(self.yaw)
            .write_byte(self.pitch)
            .write("?", self.on_ground)
        )


class PlayEntityRotation(ClientBoundPacket):
    """Sent by the server when an entity rotates. (Server -> Client)

    :param int entity_id: The ID of the entity.
    :param int yaw: The new yaw angle, the value being x/256 of a full rotation.
    :param int pitch: The new pitch angle, the value being x/256 of a full rotation.
    :param bool on_ground: Whether entity is on ground or not.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar yaw:
    :ivar pitch:
    :ivar on_ground:
    """

    id = 0x2B

    def __init__(self, entity_id: int, yaw: int, pitch: int, on_ground: bool):
        super().__init__()

        self.entity_id = entity_id
        self.yaw = yaw
        self.pitch = pitch
        self.on_ground = on_ground

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_varint(self.entity_id)
            .write("b", self.yaw)
            .write("b", self.pitch)
            .write("?", self.on_ground)
        )


class PlayRemoveEntityEffect(ClientBoundPacket):
    """Sent by the server to remove an entity's effect. (Server -> Client)

    :param int entity_id: The new yaw angle, the value being x/256 of a full rotation.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    """

    id = 0x3B

    def __init__(self, entity_id: int, effect_id: int):
        super().__init__()

        self.entity_id = entity_id
        self.effect_id = effect_id

    def pack(self) -> Buffer:
        return Buffer().write_varint(self.entity_id).write("b", self.effect_id)


class PlayEntityHeadLook(ClientBoundPacket):
    """Changes the horizontal direction an entity's head is facing. (Server -> Client)

    :param int entity_id: The ID of the entity.
    :param int head_yaw: The new head yaw angle, the value being x/256 of a full rotation.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar head_yaw:
    """

    id = 0x3E

    def __init__(self, entity_id: int, head_yaw: int):
        super().__init__()

        self.entity_id = entity_id
        self.head_yaw = head_yaw

    def pack(self) -> Buffer:
        return Buffer().write_varint(self.entity_id).write("B", self.head_yaw)


class PlayAttachEntity(ClientBoundPacket):
    """Sent when one entity has been leashed to another entity. (Server -> Client)

    :param int attached_entity_id: The ID of the entity attached to the leash.
    :param int holding_entity_id: The ID of the entity holding the leash.
    :ivar int id: Unique packet ID.
    :ivar attached_entity_id:
    :ivar holding_entity_id:
    """

    id = 0x4E

    def __init__(self, attached_entity_id: int, holding_entity_id: int):
        super().__init__()

        self.attached_entity_id = attached_entity_id
        self.holding_entity_id = holding_entity_id

    def pack(self) -> Buffer:
        return Buffer().write("i", self.attached_entity_id).write("i", self.holding_entity_id)


class PlayEntityVelocity(ClientBoundPacket):
    """Sends the velocity of an entity in units of 1/8000 of a block per server tick. (Server -> Client)

    :param int entity_id: The ID of the entity.
    :param int velocity_x: The velocity in units of 1/8000 of a block per server tick in the x axis.
    :param int velocity_y: The velocity in units of 1/8000 of a block per server tick in the y axis.
    :param int velocity_z: The velocity in units of 1/8000 of a block per server tick in the z axis.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar velocity_x:
    :ivar velocity_y:
    :ivar velocity_z:
    """

    id = 0x4F

    def __init__(self, entity_id: int, velocity_x: int, velocity_y: int, velocity_z: int):
        super().__init__()

        self.entity_id = entity_id
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.velocity_z = velocity_z

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_varint(self.entity_id)
            .write("h", self.velocity_x)
            .write("h", self.velocity_y)
            .write("h", self.velocity_z)
        )


class PlayEntityTeleport(ClientBoundPacket):
    """Sent when an entity moves more than 8 blocks. (Server -> Client)

    :param int entity_id: The ID of the entity.
    :param float x: The new x coordinate of the entity.
    :param float y: The new y coordinate of the entity.
    :param float z: The new z coordinate of the entity.
    :param int yaw: The new yaw angle, the value being x/256 of a full rotation.
    :param int pitch: The new pitch angle, the value being x/256 of a full rotation.
    :param bool on_ground: Whether or not the entity is on the ground.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar x:
    :ivar y:
    :ivar z:
    :ivar on_ground:
    """

    id = 0x62

    def __init__(
        self, entity_id: int, x: float, y: float, z: float, yaw: int, pitch: int, on_ground: bool
    ):
        super().__init__()

        self.entity_id = entity_id
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.on_ground = on_ground

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_varint(self.entity_id)
            .write("d", self.x)
            .write("d", self.y)
            .write("d", self.z)
            .write("i", self.yaw)
            .write("i", self.pitch)
            .write("?", self.on_ground)
        )


class PlayDestroyEntities(ClientBoundPacket):
    """Sent by the server when one or more entities are to be destroyed on the client. (Server -> Client)

    :param List[int] entity_ids: List of entity IDs for the client to destroy.
    :ivar int id: Unique packet ID.
    :ivar entity_ids:
    """

    id = 0x3A

    def __init__(self, entity_ids: List[int]):
        super().__init__()

        self.entity_ids = entity_ids

    def pack(self) -> Buffer:
        buf = Buffer().write_varint(len(self.entity_ids))

        for entity_id in self.entity_ids:
            buf.write_varint(entity_id)

        return buf


class PlayEntityMetadata(ClientBoundPacket):
    """Updates one or more metadata properties for an existing entity. (Server -> Client)

    :param int entity_id: The ID of the entity the data is for.
    :param Dict[Tuple[int, int], object] metadata: The entity metadata, see here: https://wiki.vg/Protocol#Entity_Metadata.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar metadata:
    """

    id = 0x4D

    def __init__(self, entity_id: int, metadata: Dict[Tuple[int, int], object]):
        super().__init__()

        self.entity_id = entity_id
        self.metadata = metadata

    def pack(self) -> Buffer:
        return Buffer().write_varint(self.entity_id).write_entity_metadata(self.metadata)


class PlayEntityEquipment(ClientBoundPacket):
    """Sends data about the entity's equipped equipment.

    :param int entity_id: The ID of the entity the equipment data is for.
    :param List[Tuple[int, Dict[str, Union[int, nbt.TAG]]]] equipment: An array of equipment, see here: https://wiki.vg/Protocol#Entity_Equipment
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar equipment:
    """

    id = 0x50

    def __init__(self, entity_id: int, equipment: List[Tuple[int, Dict[str, Union[int, nbt.TAG]]]]):
        super().__init__()

        self.entity_id = entity_id
        self.equipment = equipment

    def pack(self) -> Buffer:
        buf = Buffer().write_varint(self.entity_id).write_varint(len(self.equipment))

        for (slot_id, equipment) in self.equipment:
            buf.write("b", slot_id).write_slot(**equipment)

        return buf


class PlayEntityProperties(ClientBoundPacket):
    """Sends information about certain attributes on an entity. (Server -> Client)

    :param int entity_id: The ID of the entity.
    :param List[dict] properties: Properties of the entity.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar properties:
    """

    id = 0x64

    def __init__(self, entity_id: int, properties: List[dict]):
        super().__init__()

        self.entity_id = entity_id
        self.properties = properties

    def pack(self) -> Buffer:
        buf = Buffer().write_varint(self.entity_id)

        for prop in self.properties:
            buf.write_string(prop["key"]).write("d", prop["value"]).write_varint(
                len(prop["modifiers"])
            )

            for prop_modifier in prop["modifiers"]:
                buf.write_modifier(prop_modifier)

        return buf
