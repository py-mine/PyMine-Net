"""Contains packets relating to client logins."""

from __future__ import annotations

from uuid import UUID

from pymine_net.types.buffer import Buffer
from pymine_net.types.chat import Chat
from pymine_net.types.packet import ClientBoundPacket, ServerBoundPacket

__all__ = (
    "LoginStart",
    "LoginEncryptionRequest",
    "LoginEncryptionResponse",
    "LoginSuccess",
    "LoginDisconnect",
)


class LoginStart(ServerBoundPacket):
    """Packet from client asking to start login process. (Client -> Server)

    :param str username: Username of the client who sent the request.
    :ivar int id: Unique packet ID.
    :ivar username:
    """

    id = 0x00

    def __init__(self, username: str):
        super().__init__()

        self.username = username

    def pack(self) -> Buffer:
        return Buffer().write_string(self.username)

    @classmethod
    def unpack(cls, buf: Buffer) -> LoginStart:
        return cls(buf.read_string())


class LoginEncryptionRequest(ClientBoundPacket):
    """Used by the server to ask the client to encrypt the login process. (Server -> Client)

    :param bytes public_key: Public key.
    :param bytes verify_token: Verify token.
    :ivar int id: Unique packet ID.
    :ivar public_key:
    """

    id = 0x01

    def __init__(self, public_key: bytes, verify_token: bytes):
        super().__init__()

        self.public_key = public_key
        self.verify_token = verify_token

    def pack(self) -> Buffer:
        return (
            Buffer()
            .write_string(" " * 20)
            .write_varint(len(self.public_key))
            .write_bytes(self.public_key)
            .write_varint(len(self.verify_token))
            .write_bytes(self.verify_token)
        )

    @classmethod
    def unpack(cls, buf: Buffer) -> LoginEncryptionRequest:
        buf.read_string()

        return cls(
            buf.read_bytes(buf.read_varint()),
            buf.read_bytes(buf.read_varint())
        )


class LoginEncryptionResponse(ServerBoundPacket):
    """Response from the client to a LoginEncryptionRequest. (Client -> Server)

    :param bytes shared_key: The shared key used in the login process.
    :param bytes verify_token: The verify token used in the login process.
    :ivar int id: Unique packet ID.
    :ivar shared_key:
    :ivar verify_token:
    """

    id = 0x01

    def __init__(self, shared_key: bytes, verify_token: bytes):
        super().__init__()

        self.shared_key = shared_key
        self.verify_token = verify_token

    def pack(self) -> Buffer:
        return Buffer().write_varint(len(self.shared_key)).write_bytes(self.shared_key).write_varint(len(self.verify_token)).write_bytes(self.verify_token)

    @classmethod
    def unpack(cls, buf: Buffer) -> LoginEncryptionResponse:
        return cls(buf.read_bytes(buf.read_varint()), buf.read_bytes(buf.read_varint()))


class LoginSuccess(ClientBoundPacket):
    """Sent by the server to denote a successfull login. (Server -> Client)

    :param UUID uuid: The UUID of the connecting player/client.
    :param str username: The username of the connecting player/client.
    :ivar int id: Unique packet ID.
    :ivar uuid:
    :ivar username:
    """

    id = 0x02

    def __init__(self, uuid: UUID, username: str):
        super().__init__()

        self.uuid = uuid
        self.username = username

    def pack(self) -> Buffer:
        return Buffer().write_uuid(self.uuid).write_string(self.username)

    @classmethod
    def unpack(cls, buf: Buffer) -> LoginSuccess:
        return cls(buf.read_uuid(), buf.read_string())


class LoginDisconnect(ClientBoundPacket):
    """Sent by the server to kick a player while in the login state. (Server -> Client)

    :param Chat reason: The reason for the disconnect.
    :ivar int id: Unique packet ID.
    """

    id = 0x00

    def __init__(self, reason: Chat):
        super().__init__()

        self.reason = reason

    def pack(self) -> Buffer:
        return Buffer().write_chat(self.reason)

    @classmethod
    def unpack(cls, buf: Buffer) -> LoginDisconnect:
        return cls(buf.read_chat())


class LoginPluginRequest(ClientBoundPacket):
    """Sent by server to implement a custom handshaking flow.

    :param int message_id: Message id, generated by the server, should be unique to the connection.
    :param str channel: Channel identifier, name of the plugin channel used to send the data.
    :param bytes data: Data that is to be sent.
    :ivar int id: Unique packet ID.
    """

    id = 0x04

    def __init__(self, message_id: int, channel: str, data: bytes):
        self.message_id = message_id
        self.channel = channel
        self.data = data

    def pack(self) -> Buffer:
        return (
            Buffer().write_varint(self.message_id).write_string(self.channel).write_bytes(self.data)
        )

    @classmethod
    def unpack(cls, buf: Buffer) -> LoginPluginRequest:
        return cls(
            buf.read_varint(),
            buf.read_string(),
            buf.read_bytes()
        )


class LoginPluginResponse(ServerBoundPacket):
    """Response to LoginPluginRequest from client.

    :param int message_id: Message id, generated by the server, should be unique to the connection.
    :param Optional[bytes] data: Optional response data, present if client understood request.
    :ivar int id: Unique packet ID.
    """

    id = 0x02

    def __init__(self, message_id: int, data: bytes = None):
        self.message_id = message_id
        self.data = data

    def pack(self) -> Buffer:
        buf = Buffer().write_varint(self.message_id)
        return buf.write_optional(buf.write_bytes, self.data)

    @classmethod
    def unpack(cls, buf: Buffer) -> LoginPluginResponse:
        return cls(buf.read_varint(), buf.read_optional(buf.read_bytes))
