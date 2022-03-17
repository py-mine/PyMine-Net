"""Contains packets related to players."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

import pymine_net.types.nbt as nbt
from pymine_net.enums import GameMode, PlayerInfoAction
from pymine_net.types.buffer import Buffer
from pymine_net.types.chat import Chat
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket
from pymine_net.types.player import Player

__all__ = (
    "PlayPlayerDigging",
    "PlayAcknowledgePlayerDigging",
    "PlayDisconnect",
    "PlayPlayerAbilitiesClientBound",
    "PlayPlayerAbilitiesServerBound",
    "PlayJoinGame",
    "PlayPlayerPositionServerBound",
    "PlayPlayerPositionAndRotationServerBound",
    "PlayPlayerPositionAndLookClientBound",
    "PlayPlayerRotation",
    "PlayPlayerMovement",
    "PlayTeleportConfirm",
    "PlayClientStatus",
    "PlayClientSettings",
    "PlayCreativeInventoryAction",
    "PlaySpectate",
    "PlayCamera",
    "PlayUpdateViewPosition",
    "PlayUpdateViewDistance",
    "PlaySetExperience",
    "PlayUpdateHealth",
    "PlayDeathCombatEvent",
    "PlayFacePlayer",
    "PlayPlayerInfo",
    "PlayRespawn",
)


class PlayPlayerDigging(ServerBoundPacket):
    """Sent by the client when the start mining a block. (Client -> Server)

    :param int status: The action the player is taking against the block, see here: https://wiki.vg/Protocol#Player_Digging.
    :param int x: The x coordinate of the block.
    :param int y: The y coordinate of the block.
    :param int z: The z coordinate of the block.
    :param int face: The face of the block that the player is mining.
    :ivar int id: Unique packet ID.
    :ivar status:
    :ivar x:
    :ivar y:
    :ivar z:
    :ivar face:
    """

    id = 0x1A

    def __init__(self, status: int, x: int, y: int, z: int, face: int):
        super().__init__()

        self.status = status
        self.x = x
        self.y = y
        self.z = z
        self.face = face

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayPlayerDigging:
        return cls(buf.read_varint(), *buf.read_position(), buf.read_byte())


class PlayAcknowledgePlayerDigging(ClientBoundPacket):
    """Sent by server to acknowledge player digging. (Server -> Client)

    :param int x: The x coordinate of where the player is digging.
    :param int y: The y coordinate of where the player is digging.
    :param int z: The z coordinate of where the player is digging.
    :param int block: The block state id of the block that is being broken/dug.
    :param int status: Value 0-2 to denote whether player should start, cancel, or finish.
    :param bool successful: True if the block was dug successfully.
    :ivar int id: Unique packet ID.
    :ivar x:
    :ivar y:
    :ivar z:
    :ivar block:
    :ivar status:
    :ivar successful:
    """

    id = 0x08

    def __init__(self, x: int, y: int, z: int, block: int, status: int, successful: bool):
        super().__init__()

        self.x = x
        self.y = y
        self.z = z
        self.block = block
        self.status = status
        self.successful = successful

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_position(self.x, self.y, self.z)
            .write_varint(self.block)
            .write_varint(self.status)
            .write("?", self.successful)
        )


class PlayDisconnect(ClientBoundPacket):
    """Sent by the server before it disconnects a client. Client assumes that server has closed the connection by the time the packet arrives. (Server -> Client)

    :param Chat reason: The reason for the kick.
    :ivar int id: Unique packet ID.
    :ivar reason:
    """

    id = 0x1A

    def __init__(self, reason: Chat):
        super().__init__()

        self.reason = reason

    def pack(self) -> Buffer:
        return Buffer().write_chat(self.reason)


class PlayPlayerAbilitiesClientBound(ClientBoundPacket):
    """Defines the player's abilities. (Server -> Client)

    :param bytes flags: Client data bitfield, see here: https://wiki.vg/Protocol#Player_Abilities_.28clientbound.29.
    :param float flying_speed: Speed at which client is flying.
    :param float fov_modifier: FOV modifier value.
    :ivar int id: Unique packet ID.
    :ivar flags:
    :ivar flying_speed:
    :ivar fov_modifier:
    """

    id = 0x30

    def __init__(self, flags: int, flying_speed: float, fov_modifier: float):
        super().__init__()

        self.flags = flags
        self.flying_speed = flying_speed
        self.fov_modifier = fov_modifier

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_byte(self.flags)
            .write("f", self.flying_speed)
            .write("f", self.fov_modifier)
        )


class PlayPlayerAbilitiesServerBound(ServerBoundPacket):
    """Tells the server whether the client is flying or not. (Client -> Server)

    :param bool flying: Whether player is flying or not.
    :ivar int id: Unique packet ID.
    :ivar flying:
    """

    id = 0x19

    def __init__(self, flying: bool):
        super().__init__()

        self.flying = flying

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayPlayerAbilitiesServerBound:
        return cls(buf.read_byte() == 0x02)


class PlayJoinGame(ClientBoundPacket):
    """Tells the client the necessary information to actually join the game. (Server -> Client)

    :param int entity_id: The player's entity ID.
    :param bool is_hardcore: Whether the world is hardcore mode or not.
    :param int gamemode: The player's gamemode.
    :param int previous_gamemode: The player's previous gamemode.
    :param List[str] dimension_names: All of the worlds/dimensions loaded on the server.
    :param nbt.TAG dimension_codec: Represents a dimension and biome registry, see here: https://wiki.vg/Protocol#Join_Game.
    :param nbt.TAG dimension: A dimension type, see here: https://wiki.vg/Protocol#Join_Game.
    :param str dimension_name: The name of the world/dimension the player is joining.
    :param int hashed_seed: First 8 bytes of SHA-256 hash of the world's seed.
    :param int max_players: Max players allowed on the server, now ignored.
    :param int view_distance: Max view distance allowed by the server (2-32).
    :param int simulation_distance: Distance to which the client will process things like entities.
    :param bool reduced_debug_info: Whether debug info should be reduced or not.
    :param bool enable_respawn_screen: Set to false when the doImmediateRespawn gamerule is true.
    :param bool is_debug: If the world is a debug world.
    :param bool is_flat: If the world is a superflat world.
    :ivar int id: Unique packet ID.
    :ivar entity_id:
    :ivar is_hardcore:
    :ivar gamemode:
    :ivar previous_gamemode:
    :ivar dimension_names:
    :ivar dimension_codec:
    :ivar dimension:
    :ivar dimension_name:
    :ivar hashed_seed:
    :ivar max_players:
    :ivar view_distance:
    :ivar simulation_distance:
    :ivar reduced_debug_info:
    :ivar enable_respawn_screen:
    :ivar is_debug:
    :ivar is_flat:
    """

    id = 0x26

    def __init__(
        self,
        entity_id: int,
        is_hardcore: bool,
        gamemode: int,
        previous_gamemode: int,
        dimension_names: List[str],
        dimension_codec: nbt.TAG,
        dimension: nbt.TAG,
        dimension_name: str,
        hashed_seed: int,
        max_players: int,
        view_distance: int,
        simulation_distance: int,
        reduced_debug_info: bool,
        enable_respawn_screen: bool,
        is_debug: bool,
        is_flat: bool,
    ):
        super().__init__()

        self.entity_id = entity_id
        self.is_hardcore = is_hardcore
        self.gamemode = gamemode
        self.previous_gamemode = previous_gamemode
        self.dimension_names = dimension_names
        self.dimension_codec = dimension_codec
        self.dimension = dimension
        self.dimension_name = dimension_name
        self.hashed_seed = hashed_seed
        self.max_players = max_players
        self.view_distance = view_distance
        self.simulation_distance = simulation_distance
        self.reduced_debug_info = reduced_debug_info
        self.enable_respawn_screen = enable_respawn_screen
        self.is_debug = is_debug
        self.is_flat = is_flat

    def pack(self) -> Buffer:
        buf = (
            Buffer()
            .write("i", self.entity_id)
            .write("?", self.is_hardcore)
            .write("B", self.gamemode)
            .write_byte(self.previous_gamemode)
            .write_varint(len(self.dimension_names))
        )

        for dimension_name in self.dimension_names:
            buf.write_string(dimension_name)

        return (
            buf.write_nbt(self.dimension_codec)
            .write_nbt(self.dimension)
            .write_string(self.dimension_name)
            .write("q", self.hashed_seed)
            .write_varint(self.max_players)
            .write_varint(self.view_distance)
            .write_varint(self.simulation_distance)
            .write("?", self.reduced_debug_info)
            .write("?", self.enable_respawn_screen)
            .write("?", self.is_debug)
            .write("?", self.is_flat)
        )


class PlayPlayerPositionServerBound(ServerBoundPacket):
    """Used by the client to update the client's position. (Client -> Server)

    :param float x: The x coordinate of where the player is.
    :param float feet_y: The y coordinate of where the player's feet are.
    :param float z: The z coordinate of where the player is.
    :param bool on_ground: Whether the player/client is on the ground or not.
    :ivar int id: Unique packet ID.
    :ivar x:
    :ivar feet_y:
    :ivar z:
    :ivar on_ground:
    """

    id = 0x11

    def __init__(self, x: float, feet_y: float, z: float, on_ground: bool):
        super().__init__()

        self.x = x
        self.feet_y = feet_y
        self.z = z
        self.on_ground = on_ground

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayPlayerPositionServerBound:
        return cls(buf.read("d"), buf.read("d"), buf.read("d"), buf.read("?"))


class PlayPlayerPositionAndRotationServerBound(ServerBoundPacket):
    """Packet sent by the client to update both position and rotation. (Client -> Server)

    :param float x: The x coordinate of where the player is.
    :param float feet_y: The y coordinate of where the player's feet are.
    :param float z: The z coordinate of where the player is.
    :param float yaw: The yaw (absolute rotation on x axis) in degrees.
    :param float pitch: The pitch (absolute rotation on y axis) in degrees.
    :param bool on_ground: Whether the player/client is on the ground or not.
    :ivar int id: Unique packet ID.
    :ivar x:
    :ivar feet_y:
    :ivar z:
    :ivar yaw:
    :ivar pitch:
    :ivar on_ground:
    """

    id = 0x12

    def __init__(
        self, x: float, feet_y: float, z: float, yaw: float, pitch: float, on_ground: bool
    ):
        super().__init__()

        self.x = x
        self.feet_y = feet_y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.on_ground = on_ground

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayPlayerPositionAndRotationServerBound:
        return cls(
            buf.read("d"),
            buf.read("d"),
            buf.read("d"),
            buf.read("f"),
            buf.read("f"),
            buf.read("?"),
        )


class PlayPlayerPositionAndLookClientBound(ClientBoundPacket):
    """Updates the player's position and looking direction. Also closes the downloading terrain screen when joining/respawning. (Server -> Client)

    :param Player player: The player that's being moved.
    :param int flags: Bit field, see https://wiki.vg/Protocol#Player_Position_And_Look_.28clientbound.29.
    :param int teleport_id: The teleport ID.
    :param bool dismount_vehicle: Whether the player should dismount their vehicle.
    """

    id = 0x38

    def __init__(self, player: Player, flags: int, teleport_id: int, dismount_vehicle: bool):
        super().__init__()

        self.player = player
        self.flags = flags
        self.teleport_id = teleport_id
        self.dismount_vehicle = dismount_vehicle

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write("d", self.player.x)
            .write("d", self.player.y)
            .write("d", self.player.z)
            .write("f", self.player.rotation.yaw)
            .write("f", self.player.rotation.pitch)
            .write_byte(self.flags)
            .write_varint(self.teleport_id)
            .write("?", self.dismount_vehicle)
        )


class PlayPlayerRotation(ServerBoundPacket):
    """Used by the client to update their rotation, see here: https://wiki.vg/Protocol#Player_Rotation. (Client -> Server)

    :param float yaw: The yaw (absolute rotation on x axis) in degrees.
    :param float pitch: The pitch (absolute rotation on y axis) in degrees.
    :param bool on_ground: Whether the player/client is on the ground or not.
    :ivar int id: Unique packet ID.
    :ivar yaw:
    :ivar pitch:
    """

    id = 0x13

    def __init__(self, yaw: float, pitch: float, on_ground: bool):
        super().__init__()

        self.yaw = yaw
        self.pitch = pitch
        self.on_ground = on_ground

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayPlayerRotation:
        return cls(buf.read("f"), buf.read("f"), buf.read("?"))


class PlayPlayerMovement(ServerBoundPacket):
    """Tells server whether client/player is on ground or not. (Client -> Server)

    :param bool on_ground: Whether the player/client is on the ground or not.
    :ivar int id: Unique packet ID.
    :ivar on_ground:
    """

    id = 0x14

    def __init__(self, on_ground: bool):
        super().__init__()

        self.on_ground = on_ground

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayPlayerMovement:
        return cls(buf.read("?"))


class PlayTeleportConfirm(ServerBoundPacket):
    """Sent by the client as a confirmation to a PlayPlayerPositionAndLookClientBound. (Client -> Server)

    :param int teleport_id: ID given by a player pos and look packet.
    :ivar int id: Unique packet ID.
    :ivar teleport_id:
    """

    id = 0x00

    def __init__(self, teleport_id: int):
        super().__init__()

        self.teleport_id = teleport_id

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayTeleportConfirm:
        return cls(buf.read_varint())


class PlayClientStatus(ServerBoundPacket):
    """Used by the client to denote when the client has either (0) clicked respawn button or (1) opened the statistics menu. (Client -> Server)

    :param int action_id: Whether client has (0) clicked respawn or (1) opened stats menu.
    :ivar int id: Unique packet ID.
    :ivar int to: Packet direction.
    :ivar action_id:
    """

    id = 0x04

    def __init__(self, action_id: int):
        super().__init__()

        self.action_id = action_id

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayClientStatus:
        return cls(buf.read_varint())


class PlayClientSettings(ServerBoundPacket):
    """Used by client to update its settings either on server join or whenever. (Client -> Server)

    :param str locale: The locale of the client, example: en_US or en_GB.
    :param int view_distance: The client's view distance.
    :param int chat_mode: The client's chat mode, see here: https://wiki.vg/Protocol#Keep_Alive_.28clientbound.29.
    :param bool chat_colors: Whether the client has chat colors enabled or not.
    :param int displayed_skin_parts: A bit mask describing which parts of the client's skin are visible.
    :param int main_hand: Either left (0) or right (1).
    :param bool enable_text_filtering: Whether or not to filter text on signs and books.
    :param bool allow_server_listings: Whether or not the client should show up in the player list on the server.
    :ivar int id: Unique packet ID.
    :ivar locale:
    :ivar view_distance:
    :ivar chat_mode:
    :ivar chat_colors:
    :ivar displayed_skin_parts:
    :ivar main_hand:
    """

    id = 0x05

    def __init__(
        self,
        locale: str,
        view_distance: int,
        chat_mode: int,
        chat_colors: bool,
        displayed_skin_parts: int,
        main_hand: int,
        enable_text_filtering: bool,
        allow_server_listings: bool,
    ):
        super().__init__()

        self.locale = locale
        self.view_distance = view_distance
        self.chat_mode = chat_mode
        self.chat_colors = chat_colors
        self.displayed_skin_parts = displayed_skin_parts
        self.main_hand = main_hand
        self.enable_text_filtering = enable_text_filtering
        self.allow_server_listings = allow_server_listings

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayClientSettings:
        return cls(
            buf.read_string(),
            buf.read_byte(),
            buf.read_varint(),
            buf.read("?"),
            buf.read("B"),
            buf.read_varint(),
            buf.read("?"),
            buf.read("?"),
        )


class PlayCreativeInventoryAction(ServerBoundPacket):
    """Sent when a client/player clicks in their inventory in creative mode. (Client -> Server)

    :param int slot_id: The inventory slot that was clicked.
    :param dict slot: The slot data for the clicked item.
    :ivar int id: Unique packet ID.
    :ivar slot_id:
    :ivar clicked_item:
    """

    id = 0x28

    def __init__(self, slot_id: int, slot: dict):
        super().__init__()

        self.slot_id = slot_id
        self.slot = slot

    @classmethod
    def unpack(cls, buf: Buffer) -> PlayCreativeInventoryAction:
        return cls(buf.read("h"), buf.read_slot())


class PlaySpectate(ServerBoundPacket):
    """Used by the client to spectate a given entity. (Client -> Server)

    :param UUID target: The target entity/player to teleport to and spectate.
    :ivar int id: Unique packet ID.
    :ivar target:
    """

    id = 0x2D

    def __init__(self, target: UUID):
        super().__init__()

        self.target = target

    @classmethod
    def unpack(cls, buf: Buffer) -> PlaySpectate:
        return cls(buf.read_uuid())


class PlayCamera(ClientBoundPacket):
    """Sets the entity that the player renders from. (Server -> Client)

    :param int camera_id: The ID of the entity to set the client's camera to.
    :ivar int id: Unique packet ID.
    :ivar camera_id:
    """

    id = 0x47

    def __init__(self, camera_id: int):
        super().__init__()

        self.camera_id = camera_id

    def pack(self) -> Buffer:
        return Buffer().write_varint(self.camera_id)


class PlayUpdateViewPosition(ClientBoundPacket):
    """Sent whenever a client crosses a chunk border and for >1 block changes in the y axis, used to determine what chunks should be loaded or unloaded. (Server -> Client)

    :param int chunk_x: x chunk coordinate of the player's position.
    :param int chunk_z: z chunk coordinate of the player's position.
    :ivar int id: Unique packet ID.
    :ivar chunk_x:
    :ivar chunk_y:
    """

    id = 0x49

    def __init__(self, chunk_x: int, chunk_z: int):
        super().__init__()

        self.chunk_x = chunk_x
        self.chunk_z = chunk_z

    def pack(self) -> Buffer:
        return Buffer().write_varint(self.chunk_x).write_varint(self.chunk_z)


class PlayUpdateViewDistance(ClientBoundPacket):
    """Sent by server when player reappears in the overworld after leaving the end. (Server -> Client)

    :param int view_distance: The render distance.
    :ivar int id: Unique packet ID.
    :ivar view_distance:
    """

    id = 0x4A

    def __init__(self, view_distance: int):
        super().__init__()

        self.view_distance = view_distance

    def pack(self) -> Buffer:
        return Buffer().write_varint(self.view_distance)


class PlaySetExperience(ClientBoundPacket):
    """Sent by the server to change a client's XP levels. (Server -> Client)

    :param float xp_bar: The value of the XP bar, between 0 and 1.
    :param int level: Level of the player.
    :param int total_xp: Total experience that the player has.
    :ivar int id: Unique packet ID.
    :ivar xp_bar:
    :ivar level:
    :ivar total_xp:
    """

    id = 0x51

    def __init__(self, xp_bar: float, level: int, total_xp: int):
        super().__init__()

        self.xp_bar = xp_bar
        self.level = level
        self.total_xp = total_xp

    def pack(self) -> Buffer:
        return Buffer().write("f", self.xp_bar).write_varint(self.level).write_varint(self.total_xp)


class PlayUpdateHealth(ClientBoundPacket):
    """Sent by server to update health, hunger, and saturation of player. (Server -> Client)

    :param float health: New health of the player.
    :param int food: New food/hunger level of the player.
    :param float food_saturation: New food/hunger saturation of the player.
    :ivar int id: Unique packet ID.
    :ivar health:
    :ivar food:
    :ivar food_saturation:
    """

    id = 0x52

    def __init__(self, health: float, food: int, food_saturation: float):
        super().__init__()

        self.health = health
        self.food = food
        self.food_saturation = food_saturation

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write("f", self.health)
            .write_varint(self.food)
            .write("f", self.food_saturation)
        )


class PlayDeathCombatEvent(ClientBoundPacket):
    """Sent by the server to display the game over / respawn screen. (Server -> Client)

    :param int player_id: Entity ID of the player killed.
    :param int killer_id: Entity ID of the entity that killed the player.
    :param Chat message: The game over / respawn message to display.
    :ivar int id: Unique packet ID.
    :ivar player_id:
    :ivar killer_id:
    :ivar message:
    """

    id = 0x35

    def __init__(self, player_id: int, killer_id: int, message: Chat):
        self.player_id = player_id
        self.killer_id = killer_id
        self.message = message

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_varint(self.player_id)
            .write("i", self.killer_id)
            .write_chat(self.message)
        )


class PlayPlayerInfo(ClientBoundPacket):
    """Sent by the server to update the user list under the tab menu. (Server -> Client)

    :param PlayerInfoAction action: The action to be taken, either add player (0), update gamemode (1), update latency (2), update display name (3), or remove player (4).
    :param List[Player] players: A list of Player objects.
    :ivar int id: Unique packet ID.
    :ivar action:
    :ivar players:
    """

    id = 0x36

    def __init__(self, action: PlayerInfoAction, players: List[Player]):
        super().__init__()

        self.action = action
        self.players = players

    def pack(self) -> Buffer:
        buf = Buffer().write_varint(self.action).write_varint(len(self.players))

        if self.action == PlayerInfoAction.ADD_PLAYER:
            for player in self.players:
                buf.write_uuid(player.uuid).write_string(player.username).write_varint(
                    len(player.properties)
                )

                for prop in player.properties:
                    buf.write_string(prop.name).write_string(prop.value).write_optional(
                        buf.write_string, prop.signature
                    )

                display_name_chat = Chat(player.display_name) if player.display_name else None
                buf.write_varint(player.gamemode).write_varint(player.latency).write_optional(
                    buf.write_chat, display_name_chat
                )

        elif self.action == PlayerInfoAction.UPDATE_GAMEMODE:
            for player in self.players:
                buf.write_uuid(player.uuid).write_varint(player.gamemode)
        elif self.action == PlayerInfoAction.UPDATE_LATENCY:
            for player in self.players:
                buf.write_uuid(player.uuid).write_varint(player.latency)
        elif self.action == PlayerInfoAction.UPDATE_DISPLAY_NAME:
            for player in self.players:
                display_name_chat = Chat(player.display_name) if player.display_name else None
                buf.write_uuid(player.uuid).write_optional(buf.write_chat, display_name_chat)
        elif self.action == PlayerInfoAction.REMOVE_PLAYER:
            for player in self.players:
                buf.write_uuid(player.uuid)


class PlayFacePlayer(ClientBoundPacket):
    """Used by the server to rotate the client player to face the given location or entity. (Server -> Client)

    :param int feet_or_eyes: Whether to aim using the head position (1) or feet (0)
    :param float tx: The x coordinate of the point to face towards.
    :param float ty: The y coordinate of the point to face towards.
    :param float tz: The z coordinate of the point to face towards.
    :param bool is_entity: If true, additional info is provided.
    :param int entity_id: The entity ID.
    :param int entity_feet_or_eyes: Same as regular feet_or_eyes.
    :ivar int id: Unique packet ID.
    :ivar feet_or_eyes:
    :ivar tx:
    :ivar ty:
    :ivar tz:
    :ivar entity_id:
    :ivar entity_feet_or_eyes:
    """

    id = 0x37

    def __init__(
        self,
        feet_or_eyes: int,
        target_x: float,
        target_y: float,
        target_z: float,
        is_entity: bool,
        entity_id: Optional[int] = None,
        entity_feet_or_eyes: Optional[int] = None,
    ):
        super().__init__()

        self.feet_or_eyes = feet_or_eyes
        self.target_x = target_x
        self.target_y = target_y
        self.target_z = target_z
        self.is_entity = is_entity
        self.entity_id = entity_id
        self.entity_feet_or_eyes = entity_feet_or_eyes

    def pack(self) -> Buffer:
        buf = (
            Buffer()
            .write_varint(self.feet_or_eyes)
            .write("d", self.target_x)
            .write("d", self.target_y)
            .write("d", self.target_z)
            .write("?", self.is_entity)
        )

        if self.is_entity:
            buf.write_varint(self.entity_id).write_varint(self.entity_feet_or_eyes)

        return buf


class PlayRespawn(ClientBoundPacket):
    """Sent to change a player's dimension. (Server -> Client)

    :param nbt.TAG dimension: A dimension defined via the dimension registry.
    :param str dimension_name: Name of the world the player entity is being spawned into.
    :param int hashed_seed: First 8 bytes of the sha-256 hash of the seed.
    :param GameMode gamemode: The current gamemode of the player entity.
    :param GameMode previous_gamemode: The previous gamemode of the player entity.
    :param bool is_debug: True if the world is a debug world.
    :param bool is_flat: Whether the new world/dimension is a superflat one or not.
    :param bool copy_metadata: If False, metadata is reset on the spawned player entity. Should be True for dimension changes, False when first spawning in.
    :ivar int id: Unique packet ID.
    :ivar dimension:
    :ivar dimension_name:
    :ivar hashed_seed:
    :ivar gamemode:
    :ivar previous_gamemode:
    :ivar is_debug:
    :ivar is_flat:
    :ivar copy_metadata:
    """

    id = 0x3D

    def __init__(
        self,
        dimension: nbt.TAG,
        dimension_name: str,
        hashed_seed: int,
        gamemode: GameMode,
        previous_gamemode: GameMode,
        is_debug: bool,
        is_flat: bool,
        copy_metadata: bool,
    ) -> None:
        super().__init__()

        self.dimension = dimension
        self.dimension_name = dimension_name
        self.hashed_seed = hashed_seed
        self.gamemode = gamemode
        self.previous_gamemode = previous_gamemode
        self.is_debug = is_debug
        self.is_flat = is_flat
        self.copy_metadata = copy_metadata

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_nbt(self.dimension)
            .write_string(self.dimension_name)
            .write("q", self.hashed_seed)
            .write("B", self.gamemode)
            .write("B", self.previous_gamemode)
            .write("?", self.is_debug)
            .write("?", self.is_flat)
            .write("?", self.copy_metadata)
        )
