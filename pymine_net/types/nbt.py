from __future__ import annotations

import gzip
import struct
from typing import List, Optional, Type

from mutf8 import decode_modified_utf8, encode_modified_utf8

__all__ = (
    "TAG",
    "TAG_End",
    "TAG_Byte",
    "TAG_Short",
    "TAG_Int",
    "TAG_Long",
    "TAG_Float",
    "TAG_Double",
    "TAG_Byte_Array",
    "TAG_String",
    "TAG_List",
    "TAG_Compound",
    "TAG_Int_Array",
    "TAG_Long_Array",
    "TYPES",
    "unpack",
)

TYPES: List[Type[TAG]] = []


def unpack(buf, root_is_full: bool = True) -> TAG_Compound:
    """
    Unpacks an NBT compound tag from a Buffer.
    - If root_is_full == True, it's expected that the root tag is prefixed with a tag ID and has a name.
    """

    try:
        data = gzip.decompress(buf)
    except gzip.BadGzipFile:
        pass
    else:
        buf.clear()
        buf.write_bytes(data)

    if root_is_full:
        buf.read_byte()
        return TAG_Compound(TAG.unpack_name(buf), TAG_Compound.unpack_data(buf))

    return TAG_Compound(None, TAG_Compound.unpack_data(buf))


class BufferUtil:
    """Reimplementation of some methods from buffer.py, needed to solve cyclic dependency issues."""

    @staticmethod
    def unpack(buf, f: str) -> object:
        unpacked = struct.unpack(">" + f, buf.read_bytes(struct.calcsize(f)))

        if len(unpacked) == 1:
            return unpacked[0]

        return unpacked

    @staticmethod
    def pack(f: str, *data: object) -> bytes:
        return struct.pack(">" + f, *data)


class TAG:
    """Base class for an NBT tag.

    :param str name: The name of the TAG.
    :ivar int id: The type ID.
    :ivar name
    """

    id = None

    def __init__(self, name: Optional[str] = None):
        self.id = self.__class__.id
        self.name = "" if name is None else name

    def pack_id(self) -> bytes:
        return BufferUtil.pack("b", self.id)

    @staticmethod
    def unpack_id(buf) -> int:
        return buf.read_byte()

    def pack_name(self) -> bytes:
        mutf8_name = encode_modified_utf8(self.name)
        return BufferUtil.pack("H", len(mutf8_name)) + mutf8_name

    @staticmethod
    def unpack_name(buf) -> str:
        return decode_modified_utf8(buf.read_bytes(buf.read("H")))

    def pack_data(self) -> bytes:
        raise NotImplementedError(self.__class__.__name__)

    @classmethod
    def unpack_data(cls, buf) -> NotImplemented:
        raise NotImplementedError(cls.__name__)

    def pack(self) -> bytes:
        return self.pack_id() + self.pack_name() + self.pack_data()

    @classmethod
    def unpack(cls, buf) -> TAG:
        cls.unpack_id(buf)
        return cls(cls.unpack_name(buf), cls.unpack_data(buf))

    def pretty(self, indent: int = 0) -> str:
        return ("    " * indent) + f'{self.__class__.__name__}("{self.name}"): {self.data}'

    def __str__(self) -> str:
        return self.pretty()

    def __repr__(self) -> str:
        return self.pretty()


class TAG_End(TAG):
    id = 0

    def __init__(self, *args):
        super().__init__(None)

    def pack_name(self) -> bytes:
        return b""

    @staticmethod
    def unpack_name(buf) -> None:
        return None

    def pack_data(self) -> bytes:
        return b""

    @staticmethod
    def unpack_data(buf) -> None:
        pass

    def pretty(self, indent: int = 0) -> str:
        return ("    " * indent) + "TAG_End(): 0"


class TAG_Byte(TAG):
    """Used to represent a TAG_Byte, stores a single signed byte.

    :param str name: The name of the TAG.
    :param int data: A signed byte.
    :int id: The type ID of the TAG.
    """

    id = 1

    def __init__(self, name: Optional[str], data: int):
        super().__init__(name)

        self.data = data

    def pack_data(self) -> bytes:
        return BufferUtil.pack("b", self.data)

    @staticmethod
    def unpack_data(buf) -> int:
        return buf.read_byte()


class TAG_Short(TAG):
    """Used to represent a TAG_Short, stores a single short (2 byte int).

    :param str name: The name of the TAG.
    :param int data: A short (2 byte int).
    :int id: The type ID of the TAG.
    """

    id = 2

    def __init__(self, name: Optional[str], data: int):
        super().__init__(name)

        self.data = data

    def pack_data(self) -> bytes:
        return BufferUtil.pack("h", self.data)

    @staticmethod
    def unpack_data(buf) -> int:
        return buf.read("h")


class TAG_Int(TAG):
    """Used to represent a TAG_Int, stores an integer (4 bytes).

    :param str name: The name of the TAG.
    :param int data: A int (4 bytes).
    :int id: The type ID of the TAG.
    """

    id = 3

    def __init__(self, name: Optional[str], data: int):
        super().__init__(name)

        self.data = data

    def pack_data(self) -> bytes:
        return BufferUtil.pack("i", self.data)

    @staticmethod
    def unpack_data(buf) -> int:
        return buf.read("i")


class TAG_Long(TAG):
    """Used to represent a TAG_Long, stores a long long (8 byte int).

    :param str name: The name of the TAG.
    :param int data: A long long (8 byte int).
    :int id: The type ID of the TAG.
    """

    id = 4

    def __init__(self, name: Optional[str], data: int):
        super().__init__(name)

        self.data = data

    def pack_data(self) -> bytes:
        return BufferUtil.pack("q", self.data)

    @staticmethod
    def unpack_data(buf) -> int:
        return buf.read("q")


class TAG_Float(TAG):
    """Used to represent a TAG_Float, stores a float (4 bytes).

    :param str name: The name of the TAG.
    :param float data: A float (4 bytes).
    :int id: The type ID of the TAG.
    """

    id = 5

    def __init__(self, name: Optional[str], data: float):
        super().__init__(name)

        self.data = data

    def pack_data(self) -> bytes:
        return BufferUtil.pack("f", self.data)

    @staticmethod
    def unpack_data(buf) -> float:
        return buf.read("f")


class TAG_Double(TAG):
    """Used to represent a TAG_Double, stores a double (8 byte float).

    :param str name: The name of the TAG.
    :param float data: A double (8 byte float).
    :int id: The type ID of the TAG.
    """

    id = 6

    def __init__(self, name: Optional[str], data: float):
        super().__init__(name)

        self.data = data

    def pack_data(self) -> bytes:
        return BufferUtil.pack("d", self.data)

    @staticmethod
    def unpack_data(buf) -> float:
        return buf.read("d")


class TAG_Byte_Array(TAG, bytearray):
    """Used to represent a TAG_Byte_Array, stores an array of bytes.

    :param str name: The name of the TAG.
    :param bytearray data: Some bytes.
    :int id: The type ID of the TAG.
    """

    id = 7

    def __init__(self, name: Optional[str], data: bytearray):
        TAG.__init__(self, name)

        if isinstance(data, str):
            print(f"WARNING: data passed was not bytes ({repr(data)})")
            data = data.encode("utf8")

        bytearray.__init__(self, data)

    def pack_data(self) -> bytes:
        return BufferUtil.pack("i", len(self)) + bytes(self)

    @staticmethod
    def unpack_data(buf) -> bytearray:
        return bytearray(buf.read_bytes(buf.read("i")))

    def pretty(self, indent: int = 0) -> str:
        return f'{" " * 4 * indent}TAG_Byte_Array("{self.name}"): [{", ".join([str(v) for v in self])}]'


class TAG_String(TAG):
    """Used to represent a TAG_String, stores a string.

    :param str name: The name of the TAG.
    :param str data: A string.
    :int id: The type ID of the TAG.
    """

    id = 8

    def __init__(self, name: Optional[str], data: str):
        super().__init__(name)

        self.data = data

    def pack_data(self) -> bytes:
        mutf8_text = encode_modified_utf8(self.data)
        return BufferUtil.pack("H", len(mutf8_text)) + mutf8_text

    @staticmethod
    def unpack_data(buf) -> str:
        return decode_modified_utf8(buf.read_bytes(buf.read("H")))

    def pretty(self, indent: int = 0) -> str:
        return f'{" " * 4 * indent}{self.__class__.__name__}("{self.name}"): {self.data}'


class TAG_List(TAG, list):
    """Represents a TAG_List, a list of nameless and typeless tagss.

    :param str name: The name of the TAG.
    :param list data: A uniform list of TAGs.
    :int id: The type ID of the TAG.
    """

    id = 9

    def __init__(self, name: Optional[str], data: List[TAG]):
        TAG.__init__(self, name)
        list.__init__(self, data)

    def pack_data(self) -> bytes:
        if len(self) > 0:
            return (
                BufferUtil.pack("b", self[0].id)
                + BufferUtil.pack("i", len(self))
                + b"".join([t.pack_data() for t in self])
            )

        return BufferUtil.pack("b", 0) + BufferUtil.pack("i", 0)

    @staticmethod
    def unpack_data(buf) -> List[TAG]:
        tag = TYPES[buf.read("b")]
        length = buf.read("i")

        return [tag(None, tag.unpack_data(buf)) for _ in range(length)]

    def pretty(self, indent: int = 0) -> str:
        tab = " " * 4 * indent
        nl = ",\n"

        return f'TAG_List("{self.name}"): [\n{nl.join([t.pretty(indent+1) for t in self])}\n{tab}]'


class TAG_Compound(TAG, dict):
    """Represents a TAG_Compound, a list of named tags.

    :param str name: The name of the TAG.
    :param list data: A list of tags.
    :int id: The type ID of the TAG.
    """

    id = 10

    def __init__(self, name: Optional[str], data: List[TAG]):
        TAG.__init__(self, name)
        dict.__init__(self, [(t.name, t) for t in data])

    @property
    def data(self):
        return self.values()

    def __setitem__(self, key: str, value: TAG):
        value.name = key
        dict.__setitem__(self, key, value)

    def update(self, *args, **kwargs):
        dict.update(self, *args, **kwargs)

        for k, v in self.items():
            v.name = k

    def pack_data(self) -> bytes:
        return b"".join([tag.pack() for tag in self.values()]) + b"\x00"

    @staticmethod
    def unpack_data(buf) -> List[TAG]:
        out = []

        while True:
            tag = TYPES[buf.read("b")]

            if tag is TAG_End:
                break

            out.append(tag(tag.unpack_name(buf), tag.unpack_data(buf)))

        return out

    def pretty(self, indent: int = 0) -> str:
        tab = " " * 4 * indent
        nl = ",\n"

        return f'{tab}TAG_Compound("{self.name}"): [\n{nl.join([t.pretty(indent + 1) for t in self.values()])}\n{tab}]'


class TAG_Int_Array(TAG, list):
    """Represents a TAG_Int_Array, a list of ints (4 bytes each).

    :param str name: The name of the TAG.
    :param list data: A list of ints (4 bytes each).
    :int id: The type ID of the TAG.
    """

    id = 11

    def __init__(self, name: Optional[str], data: list):
        TAG.__init__(self, name)
        list.__init__(self, data)

    def pack_data(self) -> bytes:
        return BufferUtil.pack("i", len(self)) + b"".join(
            [BufferUtil.pack("i", num) for num in self]
        )

    @staticmethod
    def unpack_data(buf) -> List[int]:
        return [buf.read("i") for _ in range(buf.read("i"))]

    def pretty(self, indent: int = 0) -> str:
        return (
            f'{" " * 4 * indent}TAG_Int_Array("{self.name}"): [{", ".join([str(v) for v in self])}]'
        )


class TAG_Long_Array(TAG, list):
    """Represents a TAG_Long_Array, a list of long longs (8 byte ints).

    :param str name: The name of the TAG.
    :param list value: A list of long longs (8 byte ints).
    :int id: The type ID of the TAG.
    """

    id = 12

    def __init__(self, name: Optional[str], data: List[int]):
        TAG.__init__(self, name)
        list.__init__(self, data)

    def pack_data(self) -> bytes:
        return BufferUtil.pack("i", len(self)) + b"".join(
            [BufferUtil.pack("q", num) for num in self]
        )

    @staticmethod
    def unpack_data(buf) -> list:
        return [buf.read("q") for _ in range(buf.read("i"))]

    def pretty(self, indent: int = 0) -> str:
        return f'{" " * 4 * indent}TAG_Long_Array("{self.name}"): [{", ".join([str(v) for v in self])}]'


TYPES.extend(
    [
        TAG_End,
        TAG_Byte,
        TAG_Short,
        TAG_Int,
        TAG_Long,
        TAG_Float,
        TAG_Double,
        TAG_Byte_Array,
        TAG_String,
        TAG_List,
        TAG_Compound,
        TAG_Int_Array,
        TAG_Long_Array,
    ]
)
