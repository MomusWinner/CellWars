

from my_app.shared.game.game_logic.core import GameWorld, Player, Stats
from my_app.shared.game.game_logic.serialize_deserialize_game_world import (
    get_game_world_json,
    json_to_game_world,
)


def test_serialization() -> None:
    game_world = GameWorld(5, 5, {1: Player(1, 111), 2: Player(2, 222)})
    json = get_game_world_json(game_world)
    assert json is not None

def test_deserialization() -> None:
    game_world = GameWorld(5, 5, {1: Player(1, 111, Stats(90)), 2: Player(2, 222, Stats(90))})
    json = get_game_world_json(game_world)
    new_game_world = json_to_game_world(json)
    assert new_game_world.player_by_tag[1].stats.coins == 90
