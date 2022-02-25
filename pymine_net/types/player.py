from __future__ import annotations

import struct
import random
from typing import Dict, List, Optional, Set
from uuid import UUID
from pymine_net.enums import ChatMode, GameMode, MainHand, SkinPart

import pymine_net.types.nbt as nbt
from pymine_net.types.vector import Vector3, Rotation


class PlayerProperty:
    __slots__ = ("name", "value", "signature")

    def __init__(self, name: str, value: str, signature: Optional[str] = None):
        self.name = name
        self.value = value
        self.signature = signature


class Player:
    def __init__(self, entity_id: int, data: nbt.TAG_Compound):
        self.entity_id = entity_id

        self._data: Dict[str, nbt.TAG] = data

        # attributes like player settings not stored in Player._data
        self.username: str = None
        self.properties: List[PlayerProperty] = []
        self.latency = -1
        self.display_name: str = None

        # attributes from PlayClientSettings packet
        self.locale: str = None
        self.view_distance: int = None
        self.chat_mode: ChatMode = ChatMode.ENABLED
        self.chat_colors: bool = True
        self.displayed_skin_parts: Set[SkinPart] = set()
        self.main_hand: MainHand = MainHand.RIGHT
        self.enable_text_filtering: bool = False
        self.allow_server_listings: bool = True

        # attributes which should never ever change while client is connected
        self.uuid = UUID(bytes=struct.pack(">iiii", *self["UUID"]))

    def __getitem__(self, key: str) -> nbt.TAG:
        return self._data[key]

    def __setitem__(self, key: str, value: object) -> None:
        self._data[key] = value

    def get(self, key: str, default: object = None) -> Optional[nbt.TAG]:
        try:
            return self[key]
        except KeyError:
            return default

    @property
    def x(self) -> float:
        return self["Pos"][0].data

    @x.setter
    def x(self, x: float) -> None:
        self["Pos"][0] = nbt.TAG_Double(None, x)

    @property
    def y(self) -> float:
        return self["Pos"][1].data

    @y.setter
    def y(self, y: float) -> None:
        self["Pos"][1] = nbt.TAG_Double(None, y)

    @property
    def z(self) -> float:
        return self["Pos"][2].data

    @z.setter
    def z(self, z: float) -> None:
        self["Pos"][2] = nbt.TAG_Double(None, z)

    @property
    def position(self) -> Vector3:
        return Vector3(*[t.data for t in self["Pos"]])

    @position.setter
    def position(self, position: Vector3) -> None:
        self["Pos"] = nbt.TAG_List("Pos", [nbt.TAG_Double(None, position.x), nbt.TAG_Double(None, position.y), nbt.TAG_Double(None, position.z)])

    @property
    def motion(self) -> Vector3:
        return Vector3(*[t.data for t in self["Motion"]])

    @motion.setter
    def motion(self, motion: Vector3) -> None:        
        self["Motion"] = nbt.TAG_List("Motion", [nbt.TAG_Double(None, motion.x), nbt.TAG_Double(None, motion.y), nbt.TAG_Double(None, motion.z)])

    @property
    def rotation(self) -> Rotation:
        return Rotation(self["Rotation"][0].data, self["Rotation"][1].data)

    @rotation.setter
    def rotation(self, rotation: Rotation) -> None:
        self["Rotation"] = nbt.TAG_List("Rotation", [nbt.TAG_Float(None, rotation.yaw), nbt.TAG_Float(None, rotation.pitch)])

    @property
    def gamemode(self) -> GameMode:
        return GameMode(self["playerGameType"].data)

    @gamemode.setter
    def gamemode(self, gamemode: GameMode) -> None:
        self["playerGameType"] = nbt.TAG_Int("playerGameType", gamemode)

    @classmethod
    def new(cls, entity_id: int, uuid: UUID, spawn: Vector3, dimension: str) -> Player:
        return cls(entity_id, cls.new_nbt(uuid, spawn, dimension))

    def __repr__(self) -> str:
        return 

    @staticmethod
    def new_nbt(uuid: UUID, spawn: Vector3, dimension: str) -> nbt.TAG:
        return nbt.TAG_Compound(
            "",
            [
                nbt.TAG_List(
                    "Pos",
                    [nbt.TAG_Double(None, spawn.x), nbt.TAG_Double(None, spawn.y), nbt.TAG_Double(None, spawn.z)],
                ),
                nbt.TAG_List(
                    "Motion",
                    [nbt.TAG_Double(None, 0), nbt.TAG_Double(None, 0), nbt.TAG_Double(None, 0)],
                ),
                nbt.TAG_List("Rotation", [nbt.TAG_Float(None, 0), nbt.TAG_Float(None, 0)]),
                nbt.TAG_Float("FallDistance", 0),
                nbt.TAG_Short("Fire", -20),
                nbt.TAG_Short("Air", 300),
                nbt.TAG_Byte("OnGround", 1),
                nbt.TAG_Byte("NoGravity", 0),
                nbt.TAG_Byte("Invulnerable", 0),
                nbt.TAG_Int("PortalCooldown", 0),
                nbt.TAG_Int_Array("UUID", struct.unpack(">iiii", uuid.bytes)),
                nbt.TAG_String("CustomName", ""),
                nbt.TAG_Byte("CustomNameVisible", 0),
                nbt.TAG_Byte("Silent", 0),
                nbt.TAG_List("Passengers", []),
                nbt.TAG_Byte("Glowing", 0),
                nbt.TAG_List("Tags", []),
                nbt.TAG_Float("Health", 20),
                nbt.TAG_Float("AbsorptionAmount", 0),
                nbt.TAG_Short("HurtTime", 0),
                nbt.TAG_Int("HurtByTimestamp", 0),
                nbt.TAG_Short("DeathTime", 0),
                nbt.TAG_Byte("FallFlying", 0),
                # nbt.TAG_Int('SleepingX', 0),
                # nbt.TAG_Int('SleepingY', 0),
                # nbt.TAG_Int('SleepingZ', 0),
                nbt.TAG_Compound("Brain", [nbt.TAG_Compound("memories", [])]),
                nbt.TAG_List(
                    "ivaributes",
                    [
                        nbt.TAG_Compound(
                            None,
                            [
                                nbt.TAG_String("Name", "generic.max_health"),
                                nbt.TAG_Double("Base", 20),
                                nbt.TAG_List("Modifiers", []),
                            ],
                        ),
                        nbt.TAG_Compound(
                            None,
                            [
                                nbt.TAG_String("Name", "generic.follow_range"),
                                nbt.TAG_Double("Base", 32),
                                nbt.TAG_List("Modifiers", []),
                            ],
                        ),
                        nbt.TAG_Compound(
                            None,
                            [
                                nbt.TAG_String("Name", "generic.knockback_resistance"),
                                nbt.TAG_Double("Base", 0),
                                nbt.TAG_List("Modifiers", []),
                            ],
                        ),
                        nbt.TAG_Compound(
                            None,
                            [
                                nbt.TAG_String("Name", "generic.movement_speed"),
                                nbt.TAG_Double("Base", 1),
                                nbt.TAG_List("Modifiers", []),
                            ],
                        ),
                        nbt.TAG_Compound(
                            None,
                            [
                                nbt.TAG_String("Name", "generic.attack_damage"),
                                nbt.TAG_Double("Base", 2),
                                nbt.TAG_List("Modifiers", []),
                            ],
                        ),
                        nbt.TAG_Compound(
                            None,
                            [
                                nbt.TAG_String("Name", "generic.armor"),
                                nbt.TAG_Double("Base", 0),
                                nbt.TAG_List("Modifiers", []),
                            ],
                        ),
                        nbt.TAG_Compound(
                            None,
                            [
                                nbt.TAG_String("Name", "generic.armor_toughness"),
                                nbt.TAG_Double("Base", 0),
                                nbt.TAG_List("Modifiers", []),
                            ],
                        ),
                        nbt.TAG_Compound(
                            None,
                            [
                                nbt.TAG_String("Name", "generic.attack_knockback"),
                                nbt.TAG_Double("Base", 0),
                                nbt.TAG_List("Modifiers", []),
                            ],
                        ),
                        nbt.TAG_Compound(
                            None,
                            [
                                nbt.TAG_String("Name", "generic.attack_speed"),
                                nbt.TAG_Double("Base", 4),
                                nbt.TAG_List("Modifiers", []),
                            ],
                        ),
                        nbt.TAG_Compound(
                            None,
                            [
                                nbt.TAG_String("Name", "generic.luck"),
                                nbt.TAG_Double("Base", 0),
                                nbt.TAG_List("Modifiers", []),
                            ],
                        ),
                    ],
                ),
                nbt.TAG_List("ActiveEffects", []),
                nbt.TAG_Int("DataVersion", 2586),
                nbt.TAG_Int("playerGameType", GameMode.SURVIVAL),
                nbt.TAG_Int("previousPlayerGameType", -1),
                nbt.TAG_Int("Score", 0),
                nbt.TAG_String("Dimension", dimension),
                nbt.TAG_Int("SelectedItemSlot", 0),
                nbt.TAG_Compound(
                    "SelectedItem",
                    [
                        nbt.TAG_Byte("Count", 1),
                        nbt.TAG_String("id", "minecraft:air"),
                        nbt.TAG_Compound("tag", []),
                    ],
                ),
                nbt.TAG_String("SpawnDimension", "overworld"),
                nbt.TAG_Int("SpawnX", spawn.x),
                nbt.TAG_Int("SpawnY", spawn.y),
                nbt.TAG_Int("SpawnZ", spawn.z),
                nbt.TAG_Byte("SpawnForced", 0),
                nbt.TAG_Int("foodLevel", 20),
                nbt.TAG_Float("foodExhaustionLevel", 0),
                nbt.TAG_Float("foodSaturationLevel", 5),
                nbt.TAG_Int("foodTickTimer", 0),
                nbt.TAG_Int("XpLevel", 0),
                nbt.TAG_Float("XpP", 0),
                nbt.TAG_Int("XpTotal", 0),
                nbt.TAG_Int("XpSeed", random.randint(-2147483648, 2147483647)),
                nbt.TAG_List("Inventory", []),
                nbt.TAG_List("EnderItems", []),
                nbt.TAG_Compound(
                    "abilities",
                    [
                        nbt.TAG_Float("walkSpeed", 0.1),
                        nbt.TAG_Float("flySpeed", 0.05),
                        nbt.TAG_Byte("mayfly", 0),
                        nbt.TAG_Byte("flying", 0),
                        nbt.TAG_Byte("invulnerable", 0),
                        nbt.TAG_Byte("mayBuild", 1),
                        nbt.TAG_Byte("instabuild", 0),
                    ],
                ),
                # nbt.TAG_Compound('enteredNetherPosition', [nbt.TAG_Double('x', 0), nbt.TAG_Double('y', 0), nbt.TAG_Double('z', 0)]),
                # nbt.TAG_Compound('RootVehicle', [
                #     nbt.TAG_Int_Array('Attach', [0, 0, 0, 0]),
                #     nbt.TAG_Compound('Entity', [])
                # ]),
                nbt.TAG_Byte("seenCredits", 0),
                nbt.TAG_Compound(
                    "recipeBook",
                    [
                        nbt.TAG_List("recipes", []),
                        nbt.TAG_List("toBeDisplayed", []),
                        nbt.TAG_Byte("isFilteringCraftable", 0),
                        nbt.TAG_Byte("isGuiOpen", 0),
                        nbt.TAG_Byte("isFurnaceFilteringCraftable", 0),
                        nbt.TAG_Byte("isFurnaceGuiOpen", 0),
                        nbt.TAG_Byte("isBlastingFurnaceFilteringCraftable", 0),
                        nbt.TAG_Byte("isBlastingFurnaceGuiOpen", 0),
                        nbt.TAG_Byte("isSmokerFilteringCraftable", 0),
                        nbt.TAG_Byte("isSmokerGuiOpen", 0),
                    ],
                ),
            ],
        )
