from my_app.shared.game.game_logic.core import GameWorld

INFO_TEXT = "{turn}\n\nКолличество денег: {money}"


def game_info(game_world: GameWorld, player_turn: bool, player_tag: int) -> str:
    if player_turn:
        turn_text = "Ваш ход"
    else:
        turn_text = "Ход противника"

    money_amount = game_world.player_by_tag[player_tag].stats.coins

    return INFO_TEXT.format(turn=turn_text, money=money_amount)
