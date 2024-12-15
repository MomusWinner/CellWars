from my_app.shared.game.game_logic.core import GameWorld

INFO_TEXT = "{turn}\n\nКолличество денег: {money}"


def game_info(game_world: GameWorld, player_turn: bool) -> str:
    if player_turn:
        turn_text = "Ваш ход"
    else:
        turn_text = "Ход противника"

    money_amount = game_world.player_by_tag[1].stats.coins
    return INFO_TEXT.format(turn=turn_text, money=money_amount)


def add_warrior_info(game_world: GameWorld, x: int, y: int, info: str) -> str:
    return ""


def add_castle_info(game_world: GameWorld, x: int, y: int, info: str) -> str:
    return ""


def add_bank_info(game_world: GameWorld, x: int, y: int, info: str) -> str:
    return ""
