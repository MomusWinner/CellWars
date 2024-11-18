from my_app.shared.game.game_logic.game_exceptions import GameException
from my_app.shared.game.game_logic.game_main import Game, GameStates
from my_app.shared.game.game_logic.serialize_deserialize_game_world import get_game_world_json


rooms: dict[str, Game] = {}


def get_game_world_json_by_room(room_id: str):
    return get_game_world_json(rooms[room_id].game_world)


def get_game(room_id:str) -> Game | None:
    if room_id in rooms:
        return rooms[room_id]
    return None


def create_room(room_id: str, user_id1: int, user_id2) -> tuple[Game, str]:
    """
    Returns:
        tuple[bool, str]: returns tuple(Game: Game, game_world: str)
    """
    game = Game(user_id1, user_id2)
    game.create_users_castle()
    rooms[room_id] = game
    return game, get_game_world_json(game.game_world)


def remove_room(room_id: str) -> bool:
    return (rooms.pop(room_id, None) is not None)


def send_command(room_id: str, command: dict):
    state: GameStates = rooms[room_id].game_step(command)
    return state
