from .base import BaseMessage
from uuid import UUID


class GetMatchMessage(BaseMessage):
    event = "get_match"
    user_id: int

    @classmethod
    def create(cls, user_id: int):
        return CreateMatchMessage(event=cls.event, user_ids=user_id)


class CreateMatchMessage(BaseMessage):
    event = "create_match"
    user_ids : list[int]

    @classmethod
    def create(cls, user_ids: list[int]):
        return CreateMatchMessage(event=cls.event, user_ids=user_ids)


class RoomIdMessage(BaseMessage):
    event = "room_id"
    room_id: str

    @classmethod
    def create(cls, room_id: str):
        return CreateMatchMessage(event=cls.event, room_id=room_id)