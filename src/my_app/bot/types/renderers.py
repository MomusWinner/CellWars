from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from aiogram.types import InlineKeyboardButton
from typing_extensions import override

from my_app.bot.types.callbacks import MovementCallback
from my_app.bot.types.game import GameTGMessage
from my_app.bot.utils.field import get_type, map_available_placements, rotate_coordinates
from my_app.shared.game.game_logic.core import GameObject, GameWorld
from my_app.shared.game.game_logic.game_main import GameObjectFabric
from my_app.shared.game.game_logic.game_objects import Bank, Castle, Warriors

T = TypeVar("T", bound="GameObject")


class GameObjectRenderer(ABC, Generic[T]):
    type_name: str = ""
    game_world: GameWorld | None
    game_message: GameTGMessage
    info_text: str = ""
    excluded_placement_objects: list[str] = []

    def __init__(self, game_message: GameTGMessage, game_world: GameWorld | None, game_object_type: type[T]) -> None:
        self.game_world = game_world
        self.game_message = game_message
        self.game_object_type = game_object_type

    def add_info(self, x: int, y: int, player_tag: int) -> None:
        if self.game_world is None:
            raise ValueError("to add info, game world is not supposed to be None")

        rotated_point = rotate_coordinates((y, x), self.game_world.cells, player_tag)
        object = self.game_world.cells[rotated_point[0]][rotated_point[1]].game_object

        if not isinstance(object, self.game_object_type):
            return

        player = object.player

        if player.team_tag == player_tag:
            type = "Союзник"
        else:
            type = "Вражеский"

        self.game_message.info += self._format_info_text(type, object)

    @abstractmethod
    def _format_info_text(self, type: str, object: T) -> str:
        pass

    def add_available_placements(self) -> None:
        new_field = map_available_placements(self.game_message.field, self.type_name, self.excluded_placement_objects)

        self.game_message.field = new_field


class WarriorsRenderer(GameObjectRenderer[Warriors]):
    type_name = "warrior"
    info_text = "\nВыбран Воин:\n  Тип: {type}\n  Колличество: {quantity}\n  Цена: {price}"
    count_info_text = "Покупка войнов\n  Колличество денег: {money}\n  Цена: {price}"
    insufficient_funds_info_text = (
        "Недостаточно средств!\n\nПокупка войнов\n  Колличество денег: {money}\n  Цена: {price}"
    )
    excluded_placement_objects = ["castle", "bank", "warrior"]
    excluded_movement_objects = ["castle", "bank"]
    possible_moves = [
        (0, 1),
        (1, 0),
        (0, -1),
        (-1, 0),
    ]

    def __init__(self, game_message: GameTGMessage, game_world: GameWorld | None = None) -> None:
        super().__init__(game_message, game_world, Warriors)

    @override
    def _format_info_text(self, type: str, object: Warriors) -> str:
        return self.info_text.format(type=type, quantity=object.count, price=GameObjectFabric.warrior_price)

    def add_count_info(self, player_tag: int) -> None:
        if self.game_world is None:
            raise ValueError("to add count info, game world is not supposed to be None")

        text = self.count_info_text.format(
            money=self.game_world.player_by_tag[player_tag].stats.coins, price=GameObjectFabric.warrior_price
        )
        self.game_message.info = text

    def add_ins_fun_info(self, player_tag: int) -> None:
        if self.game_world is None:
            raise ValueError("to add count info, game world is not supposed to be None")

        text = self.insufficient_funds_info_text.format(
            money=self.game_world.player_by_tag[player_tag].stats.coins, price=GameObjectFabric.warrior_price
        )
        self.game_message.info = text

    def add_available_moves(self, x: int, y: int, player_tag: int) -> bool:
        if self.game_world is None:
            raise ValueError("to add moves, game world is not supposed to be None")

        len_y = len(self.game_message.field)
        len_x = len(self.game_message.field[0])

        ry, rx = rotate_coordinates((y, x), self.game_message.field, player_tag)
        warriors = self.game_world.cells[ry][rx].game_object
        if warriors is None or warriors.player.team_tag != player_tag:
            return False

        for point in self.possible_moves:
            px = x + point[1]
            py = y + point[0]

            if py >= len_y or px >= len_x or py < 0 or px < 0:
                continue

            rpy, rpx = rotate_coordinates((py, px), self.game_message.field, player_tag)
            object = self.game_world.cells[rpy][rpx].game_object
            if (
                object is not None
                and object.player.team_tag == player_tag
                and get_type(object) in self.excluded_movement_objects
            ):
                continue

            self.game_message.field[py][px] = InlineKeyboardButton(
                text=self.game_message.field[py][px].text + "🟡",
                callback_data=MovementCallback(cell_x=px, cell_y=py, type=self.type_name).pack(),
            )
        return True


class BankRenderer(GameObjectRenderer[Bank]):
    type_name = "bank"
    info_text = "\nВыбран Банк:\n  Тип: {type}\n  ХП: {hp}\n  Цена: {price}"
    excluded_placement_objects = ["castle", "bank", "warrior"]

    def __init__(self, game_message: GameTGMessage, game_world: GameWorld | None = None) -> None:
        super().__init__(game_message, game_world, Bank)

    @override
    def _format_info_text(self, type: str, object: Bank) -> str:
        return self.info_text.format(type=type, hp=object.hp, price=GameObjectFabric.warrior_price)


class CastleRenderer(GameObjectRenderer[Castle]):
    type_name = "castle"
    info_text = "\nВыбран Замок:\n  Тип: {type}\n  ХП: {hp}"

    def __init__(self, game_message: GameTGMessage, game_world: GameWorld | None = None) -> None:
        super().__init__(game_message, game_world, Castle)

    @override
    def _format_info_text(self, type: str, object: Castle) -> str:
        return self.info_text.format(type=type, hp=object.hp)

    @override
    def add_available_placements(self) -> None:
        pass
