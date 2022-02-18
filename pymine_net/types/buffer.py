from __future__ import annotations

from typing import Callable, Optional, Tuple, Union
import struct
import json
import uuid

from pymine_net.enums import Direction, EntityModifier, Pose
from pymine_net.types.chat import Chat
from pymine_net.types.registry import Registry
from pymine_net.types import nbt

__all__ = ("Buffer",)


class Buffer(bytearray):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos = 0

    def write_bytes(self, data: Union[bytes, bytearray]) -> Buffer:
        """Writes bytes to the buffer."""

        self.extend(data)

        return self

    def read_bytes(self, length: int = None) -> bytearray:
        """Reads bytes from the buffer, if length is None then all bytes are read."""

        if length is None:
            length = len(self)

        try:
            return self[self.pos : self.pos + length]
        finally:
            self.pos += length

    def clear(self) -> None:
        """Resets the position and clears the bytearray."""

        super().clear()
        self.pos = 0

    def reset(self) -> None:
        """Resets the position in the buffer."""

        self.pos = 0

    def read_byte(self) -> int:
        """Reads a singular byte as an integer from the buffer."""

        byte = self[self.pos]
        self.pos += 1
        return byte

    def write_byte(self, value: int) -> Buffer:
        """Writes a singular byte to the buffer."""

        self.extend(struct.pack(">b", value))
        return self

    def read(self, fmt: str) -> Union[object, Tuple[object]]:
        """Using the given format, reads from the buffer and returns the unpacked value."""

        unpacked = struct.unpack(">" + fmt, self.read_bytes(struct.calcsize(fmt)))

        if len(unpacked) == 1:
            return unpacked[0]

        return unpacked

    def write(self, fmt: str, *value: object) -> Buffer:
        """Using the given format and value, packs the value and writes it to the buffer."""

        self.write_bytes(struct.pack(">" + fmt, *value))
        return self

    def read_optional(self, reader: Callable) -> Optional[object]:
        """Reads an optional value from the buffer."""

        if self.read("?"):
            return reader()

    def write_optional(self, writer: Callable, value: object = None) -> Buffer:
        """Writes an optional value to the buffer."""

        if value is None:
            self.write("?", False)
        else:
            self.write("?", True)
            writer(value)

        return self

    def read_varint(self, max_bits: int = 32) -> int:
        """Reads a varint from the buffer."""

        value = 0

        for i in range(10):
            byte = self.read("B")
            value |= (byte & 0x7F) << 7 * i

            if not byte & 0x80:
                break

        if value & (1 << 31):
            value -= 1 << 32

        value_max = (1 << (max_bits - 1)) - 1
        value_min = -1 << (max_bits - 1)

        if not (value_min <= value <= value_max):
            raise ValueError(
                f"Value doesn't fit in given range: {value_min} <= {value} < {value_max}"
            )

        return value

    def write_varint(self, value: int, max_bits: int = 32) -> Buffer:
        """Writes a varint to the buffer."""

        value_max = (1 << (max_bits - 1)) - 1
        value_min = -1 << (max_bits - 1)

        if not (value_min <= value <= value_max):
            raise ValueError(
                f"num doesn't fit in given range: {value_min} <= {value} < {value_max}"
            )

        if value < 0:
            value += 1 << 32

        for _ in range(10):
            byte = value & 0x7F
            value >>= 7

            self.write("B", byte | (0x80 if value > 0 else 0))

            if value == 0:
                break

        return self

    def read_optional_varint(self) -> Optional[int]:
        """Reads an optional (None if not present) varint from the buffer."""

        value = self.read_varint()

        if value == 0:
            return None

        return value - 1

    def write_optional_varint(self, value: int = None) -> Buffer:
        """Writes an optional (None if not present) varint to the buffer."""

        return self.write_varint(0 if value is None else value + 1)

    def read_string(self) -> str:
        """Reads a UTF8 string from the buffer."""

        return self.read_bytes(self.read_varint(max_bits=16)).decode("utf-8")

    def write_string(self, value: str) -> Buffer:
        """Writes a string in UTF8 to the buffer."""

        encoded = value.encode("utf-8")
        self.write_varint(len(encoded), max_bits=16).write_bytes(encoded)

        return self

    def read_json(self) -> object:
        """Reads json data from the buffer."""

        return json.loads(self.read_string())

    def write_json(self, value: object) -> Buffer:
        """Writes json data to the buffer."""

        return self.write_string(json.dumps(value))

    def read_nbt(self) -> nbt.TAG_Compound:
        """Reads an nbt tag from the buffer."""

        return nbt.unpack(self[self.pos :])

    def write_nbt(self, value: nbt.TAG = None) -> Buffer:
        """Writes an nbt tag to the buffer."""

        if value is None:
            self.write_byte(0)
        else:
            self.write_bytes(value.pack())

        return self

    def read_uuid(self) -> uuid.UUID:
        """Reads a UUID from the buffer."""

        return uuid.UUID(bytes=self.read_bytes(16))

    def write_uuid(self, value: uuid.UUID) -> Buffer:
        """Writes a UUID to the buffer."""

        return self.write_bytes(value.bytes)

    def read_position(self) -> Tuple[int, int, int]:
        """Reads a Minecraft position (x, y, z) from the buffer."""

        def from_twos_complement(num, bits):
            if num & (1 << (bits - 1)) != 0:
                num -= 1 << bits

            return num

        data = self.read("Q")

        return (
            from_twos_complement(data >> 38, 26),
            from_twos_complement(data & 0xFFF, 12),
            from_twos_complement(data >> 12 & 0x3FFFFFF, 26),
        )

    def read_chat(self) -> Chat:
        """Reads a chat message from the buffer."""

        return Chat(self.read_json())

    def write_chat(self, value: Chat) -> Buffer:
        """Writes a chat message to the buffer."""

        return self.write_json(value.data)

    def write_position(self, x: int, y: int, z: int) -> Buffer:
        """Writes a Minecraft position (x, y, z) to the buffer."""

        def to_twos_complement(num, bits):
            return num + (1 << bits) if num < 0 else num

        return self.write(
            "Q",
            to_twos_complement(x, 26)
            << 38 + to_twos_complement(z, 26)
            << 12 + to_twos_complement(y, 12),
        )

    def read_slot(self, registry: Registry) -> dict:
        """Reads an inventory / container slot from the buffer."""

        has_item_id = self.read_optional(self.read_varint)

        if has_item_id is None:
            return {"item": None}

        return {
            "item": registry.decode(self.read_varint()),
            "count": self.read("b"),
            "tag": self.read_nbt(),
        }

    def write_slot(
        self, registry: Registry, item: str = None, count: int = 1, tag: nbt.TAG = None
    ) -> Buffer:
        """Writes an inventory / container slot to the buffer."""

        item_id = registry.encode(item)

        if item_id is None:
            self.write("?", False)
        else:
            self.write("?", True).write_varint(item_id).write("b", count).write_nbt(tag)

    def read_rotation(self) -> Tuple[float, float, float]:
        """Reads a rotation from the buffer."""

        return self.read("fff")

    def write_rotation(self, x: float, y: float, z: float) -> Buffer:
        """Writes a rotation to the buffer."""

        return self.write("fff", x, y, z)

    def read_direction(self) -> Direction:
        """Reads a direction from the buffer."""

        return Direction(self.read_varint())

    def write_direction(self, value: Direction) -> Buffer:
        """Writes a direction to the buffer."""

        return self.write_varint(value.value)

    def read_pose(self) -> Pose:
        """Reads a pose from the buffer."""

        return Pose(self.read_varint())

    def write_pose(self, value: Pose) -> Buffer:
        """Writes a pose to the buffer."""

        return self.write_varint(value.value)

    def write_recipe_item(self, value: Union[dict, str]) -> Buffer:
        """Writes a recipe item / slot to the buffer."""

        if isinstance(value, dict):
            self.write_slot(**value)
        elif isinstance(value, str):
            self.write_slot(value)
        else:
            raise TypeError(f"Invalid type {type(value)}.")

        return self

    def write_ingredient(self, value: dict) -> Buffer:
        """Writes a part of a recipe to the buffer."""

        self.write_varint(len(value))

        for slot in value.values():
            self.write_recipe_item(slot)

    def write_recipe(self, recipe_id: str, recipe: dict) -> Buffer:
        """Writes a recipe to the buffer."""

        recipe_type = recipe["type"]

        self.write_string(recipe_type).write_string(recipe_id)

        if recipe.get("group") is None:
            recipe["group"] = "null"

        if recipe_type == "minecraft:crafting_shapeless":
            print(recipe.get("ingredients"))

            self.write_string(recipe["group"]).write_varint(len(recipe["ingredients"]))

            for ingredient in recipe.get("ingredients", []):
                self.write_ingredient(ingredient)

            self.write_recipe_item(recipe["result"])
        elif recipe_type == "minecraft:crafting_shaped":
            self.write_varint(len(recipe["patern"][0])).write_varint(
                len(recipe["pattern"])
            ).write_string(recipe["group"])

            for ingredient in recipe.get("ingredients", []):
                self.write_ingredient(ingredient)

            self.write_recipe_item(recipe["result"])
        elif recipe_type[10:] in ("smelting", "blasting", "campfire_cooking"):
            print(recipe)

            (
                self.write_string(recipe["group"])
                .write_ingredient(recipe["ingredient"])
                .write_recipe_item(recipe["result"])
                .write("f", recipe["experience"])
                .write(recipe["cookingtime"])
            )
        elif recipe_type == "minecraft:stonecutting":
            self.write_string(recipe["group"]).write_ingredient(
                recipe["ingredient"]
            ).write_recipe_item(recipe["result"])
        elif recipe_type == "minecraft:smithing":
            self.write_ingredient(recipe["base"]).write_ingredient(
                recipe["addition"]
            ).write_ingredient(recipe["result"])

        return self

    def read_villager(self) -> dict:
        """Reads villager data from the buffer."""

        return {
            "kind": self.read_varint(),
            "profession": self.read_varint(),
            "level": self.read_varint(),
        }

    def write_villager(self, kind: int, profession: int, level: int) -> Buffer:
        return self.write_varint(kind).write_varint(profession).write_varint(level)

    def write_trade(
        self,
        in_item_1: dict,
        out_item: dict,
        disabled: bool,
        num_trade_usages: int,
        max_trade_usages: int,
        xp: int,
        special_price: int,
        price_multi: float,
        demand: int,
        in_item_2: dict = None,
    ) -> Buffer:
        self.write_slot(**in_item_1).write_slot(**out_item)

        if in_item_2 is not None:
            self.write("?", True).write_slot(**in_item_2)
        else:
            self.write("?", False)

        return (
            self.write("?", disabled)
            .write("i", num_trade_usages)
            .write("i", max_trade_usages)
            .write("i", xp)
            .write("i", special_price)
            .write("f", price_multi)
            .write("i", demand)
        )

    def read_particle(self) -> dict:
        particle = {}
        particle_id = particle["id"] = self.read_varint()

        if particle_id == 3 or particle_id == 23:
            particle["block_state"] = self.read_varint()
        elif particle_id == 14:
            particle["red"] = self.read("f")
            particle["green"] = self.read("f")
            particle["blue"] = self.read("f")
            particle["scale"] = self.read("f")
        elif particle_id == 32:
            particle["item"] = self.read_slot()

        return particle

    def write_particle(self, **value) -> Buffer:
        particle_id = value["particle_id"]

        if particle_id == 3 or particle_id == 23:
            self.write_varint(value["block_state"])
        elif particle_id == 14:
            self.write("ffff", value["red"], value["green"], value["blue"], value["scale"])
        elif particle_id == 32:
            self.write_slot(**value["item"])

        return self

    def write_entity_metadata(self, value: dict) -> Buffer:
        #  index, type, value
        for (i, t), v in value.items():
            self.write("B", i).write_varint(t)

            if t == 0:
                self.write("b", v)
            elif t == 1:
                self.write_varint(v)
            elif t == 2:
                self.write("f", v)
            elif t == 3:
                self.write_string(v)
            elif t == 4:
                self.write_chat(v)
            elif t == 5:
                self.write_optional(self.write_chat, v)
            elif t == 6:
                self.write_slot(**v)
            elif t == 7:
                self.write("?", v)
            elif t == 8:
                self.write_rotation(*v)
            elif t == 9:
                self.write_position(*v)
            elif t == 10:
                self.write("?", v is not None)
                if v is not None:
                    self.write_position(*v)
            elif t == 11:
                self.write_direction(v)
            elif t == 12:
                self.write_optional(self.write_uuid, v)
            elif t == 13:
                self.write_block(v)
            elif t == 14:
                self.write_nbt(v)
            elif t == 15:
                self.write_particle(**v)
            elif t == 16:
                self.write_villager(*v)
            elif t == 17:
                self.write_optional_varint(v)
            elif t == 18:
                self.write_pose(v)

        self.write_bytes(b"\xFE")

        return self

    def read_modifier(self) -> Tuple[uuid.UUID, float, EntityModifier]:
        return (self.read_uuid(), self.read("f"), EntityModifier(self.read("b")))

    def write_modifier(self, uuid_: uuid.UUID, amount: float, operation: EntityModifier):
        return self.write_uuid(uuid_).write("f", amount).write("b", operation)

    def write_node(self, node: dict) -> Buffer:
        node_flags = node["flags"]
        self.write_byte(node_flags).write_varint(len(node["children"]))

        for child in node["children"]:
            self.write_node(child)

        if node_flags & 0x08:
            self.write_varint(node["redirect_node"])

        if 1 >= node_flags & 0x03 <= 2:  # argument or literal node
            self.write_string(node["name"])

        if node_flags & 0x3 == 2:  # argument node
            self.write_string(node["parser"])

            if node.get("properties"):
                for writer, data in node["properties"]:
                    writer(data)

        if node_flags & 0x10:
            self.write_string(node["suggestions_type"])

        return self
