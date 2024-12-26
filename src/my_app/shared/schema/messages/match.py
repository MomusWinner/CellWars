from .base import BaseMessage

MATCH_MESSAGE_EVENT = "match_message"


class MatchMessage(BaseMessage):
    action: str  # search or stop_search
    user_id: int


def create_match_message(action: str, user_id: int) -> MatchMessage:
    return MatchMessage(event=MATCH_MESSAGE_EVENT, action=action, user_id=user_id)


CREATE_MATCH_MESSAGE_EVENT = "create_match"


class CreateMatchMessage(BaseMessage):
    user_ids: list[int]


def create_create_match_message(user_ids: list[int]) -> CreateMatchMessage:
    return CreateMatchMessage(event=CREATE_MATCH_MESSAGE_EVENT, user_ids=user_ids)


ROOM_ID_MESSAGE_EVENT = "room_id"


class RoomIdMessage(BaseMessage):
    room_id: str


def create_room_id_message(room_id: str) -> RoomIdMessage:
    return RoomIdMessage(event=ROOM_ID_MESSAGE_EVENT, room_id=room_id)


ROOM_CREATED_MESSAGE_EVENT = "room_id"


class RoomCreatedMessage(BaseMessage):
    room_id: str
    user_id_turn: int
    game_world: str


def create_room_created_message(room_id: str, game_world: str, user_id_turn: int) -> RoomCreatedMessage:
    return RoomCreatedMessage(
        event=ROOM_CREATED_MESSAGE_EVENT, room_id=room_id, game_world=game_world, user_id_turn=user_id_turn
    )
