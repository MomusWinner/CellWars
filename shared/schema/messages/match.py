from .base import BaseMessage


class GetMatchMessage(BaseMessage):
    user_id: int


class CreateMatchMessage(BaseMessage):
    user_ids : list[int]