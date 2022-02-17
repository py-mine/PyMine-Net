import pytest
import json
import sys
import os

# fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymine_net.types.buffer import Buffer
import pymine_net.types.nbt as nbt


VAR_INT_ERR_MSG = "Value doesn't fit in given range"
VAR_INT_MAX = (1 << 31) - 1
VAR_INT_MIN = -(1 << 31)


def test_io():
    buf = Buffer()

    assert buf == b""
    assert buf.pos == 0

    buf = Buffer(b"\x02\x69\x00\x01\x02\x03")

    assert buf.read_byte() == b"\x02"[0]
    assert buf.read_bytes(1) == b"\x69"
    assert buf.read_bytes(2) == b"\x00\x01"
    assert buf.read_bytes() == b"\x02\x03"

    buf.reset()
    assert buf.read_bytes() == b"\x02\x69\x00\x01\x02\x03"
    buf.reset()


def test_basic():
    buf = Buffer()

    assert buf.write("i", 123).write("b", 1).write("?", True).write("q", 1234567890456) == buf
    assert buf == b"\x00\x00\x00{\x01\x01\x00\x00\x01\x1fq\xfb\x06\x18"

    assert buf.read("i") == 123
    assert buf.read("b") == 1
    assert buf.read("?") is True
    assert buf.read("q") == 1234567890456


@pytest.mark.parametrize(
    "varint, error_msg",
    (
        [0, None],
        [1, None],
        [2, None],
        [3749146, None],
        [-1, None],
        [-2, None],
        [-3, None],
        [-3749146, None],
        [VAR_INT_MAX, None],
        [VAR_INT_MAX + 1, VAR_INT_ERR_MSG],
        [VAR_INT_MIN, None],
        [VAR_INT_MIN - 1, VAR_INT_ERR_MSG],
    ),
)
def test_varint(varint, error_msg):
    buf = Buffer()

    if error_msg:
        with pytest.raises(ValueError) as err:
            buf.write_varint(varint)
            assert error_msg in str(err)
    else:
        buf.write_varint(varint)
        assert buf.read_varint() == varint


def test_optional_varint():
    buf = Buffer()

    buf.write_optional_varint(1)
    buf.write_optional_varint(2)
    buf.write_optional_varint(None)
    buf.write_optional_varint(3)
    buf.write_optional_varint(None)

    assert buf.read_optional_varint() == 1
    assert buf.read_optional_varint() == 2
    assert buf.read_optional_varint() is None
    assert buf.read_optional_varint() == 3
    assert buf.read_optional_varint() is None


def test_string():
    buf = Buffer()

    buf.write_string("")
    buf.write_string("")
    buf.write_string("2")
    buf.write_string("adkfj;adkfa;ldkfj\x01af\t\n\n00;\xc3\x85\xc3\x84\xc3\x96")
    buf.write_string("")
    buf.write_string("BrUh")
    buf.write_string("")

    assert buf.read_string() == ""
    assert buf.read_string() == ""
    assert buf.read_string() == "2"
    assert buf.read_string() == "adkfj;adkfa;ldkfj\x01af\t\n\n00;\xc3\x85\xc3\x84\xc3\x96"
    assert buf.read_string() == ""
    assert buf.read_string() == "BrUh"
    assert buf.read_string() == ""


def test_json():
    buf = Buffer()

    with open(os.path.join("tests", "sample_data", "test.json")) as test_file:
        data = json.load(test_file)
        buf.write_json(data)

    for key, value in buf.read_json().items():
        assert key in data
        assert data[key] == value
