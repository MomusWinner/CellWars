from my_app.shared.game.game_logic.command import GameCommand
from my_app.shared.game.game_logic.game_main import GameStates
from my_app.shared.schema.messages.base import BaseMessage

GAME_MESSAGE_EVENT = "game_message"


class GameMessage(BaseMessage):
    room_id: str
    command: GameCommand


GAME_INFO_MESSAGE_EVENT = "game_info_message"


class GameInfoMessage(BaseMessage):
    game_state: int
    game_world: str | None  # json # GameStates.RUN
    winner_id: int | None  # GameStates.COMPLETE
    exception_code: int | None  # GameStates.ERROR
    user_id_turn: int  # user tg id


def create_game_message(room_id: str, command: GameCommand) -> GameMessage:
    return GameMessage(event=GAME_MESSAGE_EVENT, room_id=room_id, command=command)


def create_game_info_message(
    game_state: GameStates,
    game_world: str | None = None,
    exception_code: int | None = None,
    winner_id: int | None = None,
    user_id_turn: int = -1,
) -> GameInfoMessage:
    return GameInfoMessage(
        event=GAME_INFO_MESSAGE_EVENT,
        game_state=game_state.value,
        game_world=game_world,
        winner_id=winner_id,
        exception_code=exception_code,
        user_id_turn=user_id_turn,
    )
