import json
from typing import Any

import my_app.shared.game.game_logic.core as core
import my_app.shared.game.game_logic.game_objects as go


def get_game_world_json(game_world: core.GameWorld) -> str:
    def default(o: Any) -> Any:
        o_dict: dict[Any, Any] = {}
        if isinstance(o, go.GameObject):
            game_object = dict(o.__dict__)
            game_object.pop("game_world")
            game_object.pop("cell")
            o_dict = game_object
        else:
            o_dict = o.__dict__
        o_dict["__type__"] = type(o).__name__
        return o_dict
    return json.dumps(game_world, default=default)


def json_to_game_world(json_string: str) -> core.GameWorld:
    def hook(g_dict: dict[Any, Any]) -> Any:
        if "__type__" not in g_dict.keys():
            return g_dict
        match g_dict["__type__"]:
            case "Position":
                return core.Position(g_dict["x"], g_dict["y"])
            case "Player":
                return core.Player(g_dict["team_tag"], g_dict["user_id"], g_dict["stats"])
            case "Cell":
                return core.Cell(g_dict["position"], g_dict["game_object"])
            case "GameWorld":
                player_by_tag: dict[Any, Any] = g_dict["player_by_tag"]
                keys = list(player_by_tag.keys())
                for key in keys:
                    player_by_tag[int(key)] = player_by_tag[key]
                    player_by_tag.pop(key)

                return core.GameWorld(
                    g_dict["width"],
                    g_dict["height"],
                    g_dict["player_by_tag"],
                    g_dict["cells"])
            case "Bank":
                return go.Bank(None, game_world=None, player=g_dict["player"], hp=g_dict["hp"])
            case "Warriors":
                return go.Warriors(None, None, player=g_dict["player"], count=g_dict["count"])
            case "Castle":
                return go.Castle(None, None, g_dict["player"], g_dict["hp"])
            case "Stats":
                stats = core.Stats()
                if "coins" in g_dict:
                    stats.coins = g_dict["coins"]
                return stats
            case _:
                raise Exception("__type__ is not defined")

    game_world: core.GameWorld = json.loads(json_string, object_hook=hook)

    for x in range(game_world.width):
        for y in range(game_world.height):
            game_object = game_world.cells[x][y].game_object
            if not isinstance(game_object, go.GameObject):
                continue
            game_object.cell = game_world.cells[x][y]
            game_object.game_world = game_world

    return game_world
