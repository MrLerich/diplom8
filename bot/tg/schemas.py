from dataclasses import field
from typing import List

import marshmallow_dataclass
from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass


@dataclass
class MessageFrom:
    """Модель пользователя бота"""
    id: int
    is_bot: bool
    first_name: str | None
    last_name: str | None
    username: str
    # language_code: str | None

    class Meta:
        unknown: str = EXCLUDE


@dataclass
class Chat:
    """Модель чата бота"""
    id: int
    first_name: str | None
    last_name: str | None
    username: str | None
    type: str

    # title: str | None

    class Meta:
        unknown: str = EXCLUDE


@dataclass
class Message:
    """Модель сообщения бота"""
    message_id: int
    msg_from: MessageFrom = field(metadata={'data_key': 'from'})  # from уже занято в python идем через alias  msg_from
    chat: Chat
    date: int
    text: str | None

    class Meta:
        unknown: str = EXCLUDE


@dataclass
class UpdateObj:
    """Модель бота полученных сообщений"""
    update_id: int
    message: Message

    class Meta:
        unknown: str = EXCLUDE


@dataclass
class GetUpdatesResponse:
    """Модель бота для получения сообщений от пользователя"""
    ok: bool
    result: List[UpdateObj]

    class Meta:
        unknown: str = EXCLUDE


@dataclass
class SendMessageResponse:
    """Модель бота для отправки сообщения"""
    ok: bool
    result: Message

    class Meta:
        unknown: str = EXCLUDE


GET_UPDATES_SCHEMA = marshmallow_dataclass.class_schema(GetUpdatesResponse)()  # готовая схема из dataclass
SEND_MESSAGE_RESPONSE_SCHEMA = marshmallow_dataclass.class_schema(SendMessageResponse)()
