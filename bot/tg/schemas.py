from dataclasses import field
from typing import (
    ClassVar,
    List,
    Optional,
    Type
)

from marshmallow import (
    EXCLUDE,
    Schema
)
from marshmallow_dataclass import dataclass


@dataclass
class MessageFrom:
    """Telegram API: https://core.telegram.org/bots/api#user"""
    id: int
    first_name: Optional[str] = field(default=None)
    last_name: Optional[str] = field(default=None)
    username: Optional[str] = field(default=None)

    class Meta:
        unknown = EXCLUDE


@dataclass
class Chat:
    id: int
    type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    title: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    """Telegram API: https://core.telegram.org/bots/api#message"""
    message_id: int
    chat: Chat
    # override usage of keyword "from" - add underscore and metadata to map to data key
    from_: Optional[MessageFrom] = field(metadata=dict(data_key='from'), default=None)
    text: Optional[str] = field(default=None)

    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    """Telegram API: https://core.telegram.org/bots/api#getting-updates"""
    update_id: int
    message: Optional[Message] = field(default=None)

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    """https://core.telegram.org/bots/api#getupdates"""
    ok: bool
    result: List[UpdateObj]
    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    """https://core.telegram.org/bots/api#sendmessage"""
    ok: bool
    result: Message
    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE
