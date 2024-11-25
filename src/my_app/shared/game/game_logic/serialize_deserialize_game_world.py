import json
from my_app.shared.game.game_logic.game_objects import *
from my_app.shared.game.game_logic.core import *

def get_game_world_json(game_world: GameWorld) -> str:
    def default(o):
        o_dict: dict = {}

        if isinstance(o, GameObject):
            game_object = dict(o.__dict__)
            game_object.pop("game_world")
            game_object.pop("cell")
            o_dict = game_object
        else:
            o_dict = o.__dict__ 
        o_dict["__type__"] = type(o).__name__
        return o_dict
    return json.dumps(game_world, default = default)


def json_to_game_world(json_string: str) -> GameWorld:
    def hook(g_dict: dict):
        if "__type__" not in g_dict.keys():
            return g_dict
        match g_dict["__type__"]:
            case "Position":
                return Position(g_dict["x"], g_dict["y"])
            case "Player":
                return Player(g_dict["team_tag"], g_dict["user_id"])
            case "Cell":
                return Cell(g_dict["position"], g_dict["game_object"])
            case "GameWorld":
                player_by_tag: dict = g_dict["player_by_tag"]
                keys = list(player_by_tag.keys())
                for key in keys:
                    player_by_tag[int(key)] = player_by_tag[key]
                    player_by_tag.pop(key)

                return GameWorld(g_dict["width"], g_dict["height"], g_dict["player_by_tag"], g_dict["cells"])
            case "Bank":
                return Bank(None, game_world=None, player=g_dict["player"], hp=g_dict["hp"])
            case "Warriors":
                return Warriors(None, None, player=g_dict["player"], count=g_dict["count"])
            case "Castle":
                return Castle(None, None, g_dict["player"], g_dict["hp"])
            case "Stats":
                stats = Stats()
                if "coins" in g_dict.keys():
                    stats.coins = g_dict["coins"]
                return stats
            case _:
                raise Exception("__type__ is not defined")



    game_world: GameWorld = json.loads(json_string, object_hook=hook)

    for x in range(game_world.width):
        for y in range(game_world.height):
            game_object = game_world.cells[x][y].game_object
            if not isinstance(game_object, GameObject):
                continue
            game_object.cell = game_world.cells[x][y]
            game_object.game_world = game_world

    return game_world
