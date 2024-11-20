from .base import BaseMessage


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


class RoomCreatedMessage(BaseMessage):
    event = "room_id"
    room_id: str
    your_turn: bool
    game_world: str

    @classmethod
    def create(cls, room_id: str, game_world: str, your_turn: bool):
        return RoomCreatedMessage(event=cls.event, room_id=room_id,
                game_world=game_world, your_turn=your_turn)
