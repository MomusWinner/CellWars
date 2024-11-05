from .base import BaseMessage
from uuid import UUID


class MatchMessage(BaseMessage):
    event = "match_message"
    action: str # search or stop_search
    user_id: int

    @classmethod
    def create(cls, action, user_id):
        return MatchMessage(event=cls.event, action=action, user_id=user_id)

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
        return RoomIdMessage(event=cls.event, room_id=room_id)
