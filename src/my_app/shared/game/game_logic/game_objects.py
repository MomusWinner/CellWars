from __future__ import annotations
from my_app.shared.game.game_logic.core import GameObject, Position, GameWorld, Cell, Player
from my_app.shared.game.game_logic.game_exceptions import IncorrectMovementPositionException
from abc import ABC

class Iterable(ABC):
    def on_iter(self):
        raise NotImplementedError("on_iter method is not implemented")


class Vulnerable(GameObject):
    hp = 10

    def __init__(self, cell, game_world, player):
        super().__init__(cell, game_world, player)

    def set_damage(self, damage: int) -> bool:
        if self.hp <= damage:
            self.hp = 0
            self.game_world.destroy(self)
            return True
        self.hp -= damage
        return False


class Building(Vulnerable):
    def __init__(self, cell, game_world, player, hp = 10):
        super().__init__(cell, game_world, player)
        self.hp = hp


class Castle(Building):
    def __init__(self, cell, game_world, player, hp = 100):
        super().__init__(cell, game_world, player, hp)

    def on_destroy(self):
        return super().on_destroy()


class Bank(Building, Iterable):
    coins_per_iter = 20

    def __init__(self, cell, game_world, player, hp = 20):
        super().__init__(cell, game_world, player, hp)

    def on_iter(self):
        self.player.stats.coins += self.coins_per_iter


class Warriors(GameObject):
    max_distance = 2

    def __init__(self, cell: Cell, game_world: GameWorld, player: Player, count: int):
        super().__init__(cell, game_world, player)
        self.count = count

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

    def _attack_vulnerable(self, vulnerable: Vulnerable):
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

    def _move(self, target: Position):
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

    def move(self, target: Position):
        if (self.game_world.distance(self.cell.position, target) > 2):
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
