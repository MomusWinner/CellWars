from __future__ import annotations

from abc import ABC, abstractmethod

from my_app.shared.game.game_logic.core import Cell, GameObject, GameWorld, Player, Position
from my_app.shared.game.game_logic.game_exceptions import IncorrectMovementPositionException


class Iterable(ABC):
    @abstractmethod
    def on_iter(self) -> None:
        raise NotImplementedError("on_iter method is not implemented")


class Vulnerable(GameObject):  # type: ignore[misc]
    hp = 10

    def __init__(self, cell: Cell, game_world: GameWorld, player: Player) -> None:
        super().__init__(cell, game_world, player)

    def set_damage(self, damage: int) -> bool:
        if self.hp <= damage:
            self.hp = 0
            self.game_world.destroy(self)
            return True
        self.hp -= damage
        return False

    def on_destroy(self) -> None:
        pass


class Building(Vulnerable):
    def __init__(self, cell: Cell, game_world: GameWorld, player: Player, hp: int = 10) -> None:
        super().__init__(cell, game_world, player)
        self.hp = hp


class Castle(Building):
    def __init__(self, cell: Cell, game_world: GameWorld, player: Player, hp: int = 100) -> None:
        super().__init__(cell, game_world, player, hp)

    def on_destroy(self) -> None:
        pass


class Bank(Building, Iterable):
    coins_per_iter = 20

    def __init__(self, cell: Cell, game_world: GameWorld, player: Player, hp: int = 20) -> None:
        super().__init__(cell, game_world, player, hp)

    def on_iter(self) -> None:
        self.player.stats.coins += self.coins_per_iter


class Warriors(GameObject):  # type: ignore[misc]
    max_distance = 1

    def __init__(self, cell: Cell, game_world: GameWorld, player: Player, count: int):
        super().__init__(cell, game_world, player)
        self.count = count

    def on_destroy(self) -> None:
        pass

    def _change_position(self, position: Position) -> None:
        self.game_world.clean_cell(self.cell.position)
        self.game_world.set_object_to_cell(position, self)

    def _fight_with_warriors(self, other_warriors: Warriors) -> None:
        other_w_position = other_warriors.cell.position

        if other_warriors.player == self.player:
            other_warriors.count += self.count
            return

        if other_warriors.count > self.count:
            other_warriors.count -= self.count
            self.game_world.destroy(self)
        elif self.count > other_warriors.count:
            self.count -= other_warriors.count
            self.game_world.destroy(other_warriors)
            self._change_position(other_w_position)
        else:
            self.game_world.destroy(self)
            self.game_world.destroy(other_warriors)

    def _attack_vulnerable(self, vulnerable: Vulnerable) -> None:
        v_pos = vulnerable.cell.position
        damage = 0
        if vulnerable.hp >= self.count:
            damage = self.count
        elif vulnerable.hp < self.count:
            damage = vulnerable.hp

        target_is_destroyed = vulnerable.set_damage(damage)
        self.count -= damage

        if self.count <= 0:
            self.game_world.destroy(self)
        elif target_is_destroyed:
            self._change_position(v_pos)

    def _move(self, target: Position) -> None:
        target_object = self.game_world.get_object_by_position(target)
        if target_object is None:
            self._change_position(target)
        elif isinstance(target_object, Warriors):
            self._fight_with_warriors(target_object)
        elif target_object.player == self.player:
            raise IncorrectMovementPositionException
        elif isinstance(target_object, Vulnerable):
            self._attack_vulnerable(target_object)
        else:
            raise IncorrectMovementPositionException

    def move(self, target: Position) -> None:
        if self.game_world.distance(self.cell.position, target) > 2:
            raise IncorrectMovementPositionException

        target_object = self.game_world.get_object_by_position(target)
        if target_object is None:
            self._change_position(target)
        elif isinstance(target_object, Warriors):
            self._fight_with_warriors(target_object)
        elif target_object.player == self.player:
            raise IncorrectMovementPositionException
        elif isinstance(target_object, Vulnerable):
            self._attack_vulnerable(target_object)
        else:
            raise IncorrectMovementPositionException
