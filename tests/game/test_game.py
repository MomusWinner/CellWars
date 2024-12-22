import pytest

import my_app.shared.game.game_logic.game_exceptions as ge
from my_app.shared.game.game_logic.command import (
    create_build_bank_command,
    create_buy_warriors_command,
    create_move_warriors_command,
)
from my_app.shared.game.game_logic.core import Position, Stats
from my_app.shared.game.game_logic.game_main import Game


def test_correct_warriors_fighting() -> None:
    user_id1 = 1234
    user_id2 = 5678
    game = Game(user_id1, user_id2, Stats(coins=100000))
    game.create_users_castle()

    game.game_step(create_buy_warriors_command(user_id1, {"x": 1, "y": 1}, 200))
    game.game_step(create_buy_warriors_command(user_id2, {"x": 1, "y": 3}, 10))
    game.game_step(create_move_warriors_command(user_id1, {"x": 1, "y": 1}, {"x": 1, "y": 3}))

    game_object = game.game_world.get_object_by_position(Position(1, 3))

    assert game_object.player.user_id == user_id1


def test_correct_winner() -> None:
    user_id1 = 1234
    user_id2 = 5678
    game = Game(user_id1, user_id2, Stats(coins=100000))
    game.create_users_castle()

    game.game_step(create_buy_warriors_command(user_id1, {"x": 1, "y": 1}, 200))
    game.game_step(create_buy_warriors_command(user_id2, {"x": 1, "y": 3}, 10))
    game.game_step(create_move_warriors_command(user_id1, {"x": 1, "y": 1}, {"x": 1, "y": 3}))
    game.game_step(create_buy_warriors_command(user_id2, {"x": 3, "y": 3}, 1))
    game.game_step(create_move_warriors_command(user_id1, {"x": 1, "y": 3}, {"x": 2, "y": 4}))
    game.game_world.print_cells()
    assert game.get_winner().user_id == user_id1


def test_raise_incorrect_zone_error() -> None:
    user_id1 = 1234
    user_id2 = 5678
    game = Game(user_id1, user_id2, Stats(coins=100000))
    game.create_users_castle()

    with pytest.raises(ge.IncorrectZone):
        game.game_step(create_buy_warriors_command(user_id1, {"x": 1, "y": 4}, 200))


def test_raise_not_enough_coins_error() -> None:
    user_id1 = 1234
    user_id2 = 5678
    game = Game(user_id1, user_id2, Stats(coins=10))
    game.create_users_castle()

    with pytest.raises(ge.NotEnoughCoinsException):
        game.game_step(create_buy_warriors_command(user_id1, {"x": 1, "y": 1}, 200))


def test_raise_incorrect_movement_position_error_movement_is_too_long() -> None:
    user_id1 = 1234
    user_id2 = 5678
    game = Game(user_id1, user_id2, Stats(coins=10000))
    game.create_users_castle()

    game.game_step(create_buy_warriors_command(user_id1, {"x": 1, "y": 1}, 200))
    game.game_step(create_buy_warriors_command(user_id2, {"x": 1, "y": 3}, 10))
    with pytest.raises(ge.IncorrectMovementPositionException):
        game.game_step(create_move_warriors_command(user_id1, {"x": 1, "y": 1}, {"x": 1, "y": 4}))


def test_raise_incorrect_movement_position_movement_err_move_to_building() -> None:
    user_id1 = 1234
    user_id2 = 5678
    game = Game(user_id1, user_id2, Stats(coins=10000))
    game.create_users_castle()

    game.game_step(create_buy_warriors_command(user_id1, {"x": 1, "y": 1}, 200))
    game.game_step(create_buy_warriors_command(user_id2, {"x": 1, "y": 3}, 10))
    game.game_step(create_build_bank_command(user_id1, {"x": 2, "y": 1}))
    game.game_step(create_buy_warriors_command(user_id2, {"x": 3, "y": 3}, 1))
    with pytest.raises(ge.IncorrectMovementPositionException):
        game.game_step(create_move_warriors_command(user_id1, {"x": 1, "y": 1}, {"x": 2, "y": 1}))
