from my_app.shared.game.game_logic.command import GameCommand
from my_app.shared.game.game_logic.game_main import GameStates
from my_app.shared.schema.messages.base import BaseMessage


class GameMessage(BaseMessage):
    event = "game_message"
    room_id: str
    command: GameCommand

    @classmethod
    def create(cls, command, room_id):
        return GameMessage(event=cls.event, command=command, room_id=room_id)


class GameInfoMessage(BaseMessage):
    event = "game_info_message"
    game_state: int
    game_world: str | None # json # GameStates.RUN
    winner_id: int | None # GameStates.COMPLETE
    exception_code: int | None # GameStates.ERROR
    your_turn: bool

    @classmethod
    def create(
        cls, game_state:GameStates,
        game_world: str | None = None, exception_code: int | None = None, 
        winner_id: int|None = None, your_turn: bool = False):
        return GameMessage(event=cls.event, winner_id=winner_id ,game_world=game_world,
            exception_code=exception_code, game_state=game_state, your_turn=your_turn)
