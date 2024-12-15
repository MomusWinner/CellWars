from .base import BaseMessage


class MatchMessage(BaseMessage):
    event = "match_message"
    action: str # search or stop_search
    user_id: int

    @classmethod
    def create(cls, action, user_id):
        return MatchMessage(event=cls.event, action=action, user_id=user_id)


class CreateMatchMessage(BaseMessage): # send to game server
    event = "create_match"
    user_ids : list[int]

    @classmethod
    def create(cls, user_ids: list[int]):
        return CreateMatchMessage(event=cls.event, user_ids=user_ids)


class RoomCreatedMessage(BaseMessage):
    event = "room_id"
    room_id: str
    user_id_turn: int  # user tg id
    game_world: str

    @classmethod
    def create(cls, room_id: str, game_world: str, user_id_turn: int):
        return RoomCreatedMessage(event=cls.event, room_id=room_id,
                game_world=game_world, user_id_turn=user_id_turn)
