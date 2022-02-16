from typing import Callable, Optional, Tuple, Union
from typing_extensions import Self
import struct
import json
import uuid

from pymine_net import nbt
from pymine_net.types.chat import Chat


BYTES_LIKE = Union[bytes, bytearray]


class Buffer(bytearray):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos = 0

    def write_bytes(self, data: BYTES_LIKE) -> Self:
        """Writes bytes to the buffer."""

        self.extend(data)

        return self

    def read_bytes(self, length: int = None) -> bytearray:
        """Reads bytes from the buffer, if length is None then all bytes are read."""

        if length is None:
            length = len(self.buf)

        try:
            return self.buf[self.pos : self.pos + length]
        finally:
            self.pos += length

    def clear(self) -> None:
        """Resets the position and clears the bytearray."""

        self.clear()
        self.pos = 0

    def reset(self) -> None:
        """Resets the position in the buffer."""

        self.pos = 0

    def read_byte(self) -> int:
        """Reads a singular byte as an integer from the buffer."""

        byte = self.buf[self.pos]
        self.pos += 1
        return byte

    def write_byte(self, value: int) -> Self:
        """Writes a singular byte to the buffer."""

        self.buf.write(struct.pack(">b", value))
        return self
    
    def read(self, fmt: str) -> Union[object, Tuple[object]]:
        """Using the given format, reads from the buffer and returns the unpacked value."""

        unpacked = struct.unpack(">" + fmt, self.read(struct.calcsize(fmt)))

        if len(unpacked) == 1:
            return unpacked[0]

        return unpacked

    def write(self, fmt: str, *value: object) -> Self:
        """Using the given format and value, packs the value and writes it to the buffer."""

        self.write_bytes(struct.pack(">" + fmt, *value))
        return self

    def read_optional(self, reader: Callable) -> Optional[object]:
        """Reads an optional value from the buffer."""

        if self.read("?"):
            return reader()

    def write_optional(self, writer: Callable, value: object = None) -> Self:
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
            raise ValueError(f"Value doesn't fit in given range: {value_min} <= {value} < {value_max}")

        return value

    def write_varint(self, value: int, max_bits: int = 32) -> Self:
        """Writes a varint to the buffer."""

        value_max = (1 << (max_bits - 1)) - 1
        value_min = -1 << (max_bits - 1)

        if not (value_min <= value <= value_max):
            raise ValueError(f"num doesn't fit in given range: {value_min} <= {value} < {value_max}")

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

    def write_optional_varint(self, value: int = None) -> Self:
        """Writes an optional (None if not present) varint to the buffer."""

        self.write_varint(0 if value is None else value + 1)
        return self

    def read_string(self) -> str:
        """Reads a UTF8 string from the buffer."""

        return self.read_bytes(self.read_varint(max_bits=16)).decode("utf-8")

    def write_string(self, value: str) -> Self:
        """Writes a string in UTF8 to the buffer."""

        encoded = value.encode("utf-8")
        self.write_varint(len(encoded), max_bits=16).write_bytes(encoded)

        return self

    def read_json(self) -> object:
        """Reads json data from the buffer."""

        return json.loads(self.read_string())

    def write_json(self, value: object) -> Self:
        """Writes json data to the buffer."""

        self.write_string(json.dumps(value))

        return self

    def read_nbt(self) -> nbt.TAG_Compound:
        """Reads an nbt tag from the buffer."""

        return nbt.unpack(self)

    def write_nbt(self, value: nbt.TAG = None) -> Self:
        """Writes an nbt tag to the buffer."""

        if value is None:
            self.write_byte(0)
        else:
            self.write_bytes(value.pack())

        return self

    def read_uuid(self) -> uuid.UUID:
        """Reads a UUID from the buffer."""

        return uuid.UUID(bytes=self.read_bytes(16))

    def write_uuid(self, value: uuid.UUID) -> Self:
        """Writes a UUID to the buffer."""

        self.write_bytes(value.bytes)

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

    def write_position(self, x: int, y: int, z: int) -> Self:
        """Writes a Minecraft position (x, y, z) to the buffer."""

        def to_twos_complement(num, bits):
            return num + (1 << bits) if num < 0 else num

        self.write("Q", to_twos_complement(x, 26) << 38 + to_twos_complement(z, 26) << 12 + to_twos_complement(y, 12))


buffer = Buffer()
buffer.write_byte(1).write_bytes(b"123abc").write_varint(420)
