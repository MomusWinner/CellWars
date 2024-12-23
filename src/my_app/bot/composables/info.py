from my_app.bot.types.game import GameTGMessage
from my_app.bot.utils.field import rotate_coordinates
from my_app.shared.game.game_logic.core import GameWorld
from my_app.shared.game.game_logic.game_objects import Bank, Castle, Warriors

INFO_TEXT = "{turn}\n\nКолличество денег: {money}"


def game_info(game_world: GameWorld, player_turn: bool, player_tag: int) -> str:
    if player_turn:
        turn_text = "Ваш ход"
    else:
        turn_text = "Ход противника"

    money_amount = game_world.player_by_tag[player_tag].stats.coins

    return INFO_TEXT.format(turn=turn_text, money=money_amount)
