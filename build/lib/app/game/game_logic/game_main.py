from __future__ import annotations
from enum import Enum
from abc import ABC
from typing import TypedDict
from game.game_logic.game_exceptions import *
from enum import Enum

class PositionCommand(TypedDict):
    x: int
    y: int


class MoveWarriorsCommand(TypedDict):
    move_from: PositionCommand 
    move_to: PositionCommand


class BuyWarriorsCommand(TypedDict):
    position: PositionCommand
    count: int


class BuildBank(TypedDict):
    position: PositionCommand


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class Cell:
    def __init__(self, position: Position, game_object: "GameObject" | None = None):
        self.position = position
        self.game_object = game_object


class GameCommands(Enum):
    MOVE_WARRIORS = 1
    BUILD = 2
    BUY_WARRIORS = 3


class GameObjectFabric:
    warrior_price = 10
    bank_price = 50

    def __init__(self, game_world: GameWorld, team_tag_to_player: dict[int, Player]):
        self.game_world = game_world
        self.team_tag_to_player = team_tag_to_player
    
    def create_warriors(self, position: Position, team_tag: int, count) -> Warriors:
        if self.game_world.cells[position.x][position.y].game_object is not None:
            raise PositionIsAlreadyBusyException
        
        warriors_price = count * self.warrior_price
        player = self.team_tag_to_player[team_tag]
        if warriors_price > player.stats.coins:
            raise NotEnoughCoinsException

        player.stats.coins -= warriors_price
        cell: Cell = self.game_world.cells[position.x][position.y]
        cell.game_object = Warriors(cell, self.game_world, player, count)
        return cell.game_object
    
    def create_castle(self, position: Position, team_tag: int) -> Castle:
        if self.game_world.cells[position.x][position.y].game_object is not None:
            raise PositionIsAlreadyBusyException
        
        player = self.team_tag_to_player[team_tag]
        if self.bank_price > player.stats.coins:
            raise NotEnoughCoinsException

        cell: Cell = self.game_world.cells[position.x][position.y]
        cell.game_object = Castle(cell, self.game_world, player)
        return cell.game_object
    
    def create_bank(self, position: Position, team_tag: int) -> Bank:
        if self.game_world.cells[position.x][position.y].game_object is not None:
            raise PositionIsAlreadyBusyException
        
        player = self.team_tag_to_player[team_tag]
        if self.bank_price > player.stats.coins:
            raise NotEnoughCoinsException
        
        player.stats.coins -= self.bank_price
        
        cell: Cell = self.game_world.cells[position.x][position.y]
        cell.game_object = Bank(cell, self.game_world, player)
        return cell.game_object


class GameWorld:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.cells = []
        for x in range(width):
            line_cells = []
            for y in range(height):
                line_cells.append(Cell(Position(x, y)))
            self.cells.append(line_cells)

    def distance(self, position1: Position, position2: Position):
        return abs(position1.x - position2.x) + abs(position1.y - position2.y)

    def get_object_by_position(self, position: Position) -> GameObject | None:
        return self.cells[position.x][position.y].game_object

    def set_object_to_cell(self, position: Position, game_object: GameObject):
        self.cells[position.x][position.y].game_object = game_object
        game_object.cell = self.cells[position.x][position.y]

    def clean_cell(self, position: Position):
        self.cells[position.x][position.y].game_object = None

    def print_cells(self):
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                game_object: GameObject = self.cells[x][y].game_object
                line += type(game_object).__name__
                if game_object is not None:
                    line += f"({game_object.player.team_tag})"
                line += "  "
            print(line+"\n")

    def find_objects_by_type(self, target_type: type):
        game_objects = []
        for x in range(self.width):
            for y in range(self.height):
                game_object = self.get_object_by_position(Position(x, y))
                if type(game_object) == target_type:
                    game_objects.append(game_object)
        
        return game_objects

    def destroy(self, game_object: GameObject):
        game_object.on_destroy()
        pos = game_object.cell.position
        self.cells[pos.x][pos.y].game_object = None
        print("Destroy " + type(game_object).__name__)


class Iterable(ABC):
    def on_iter(self):
        raise NotImplementedError("on_iter method is not implemented")


class GameObject(ABC):
    def __init__(self, cell: Cell, game_world: GameWorld, player: Player):
        self.cell = cell
        self.game_world = game_world
        self.player = player

    def on_destroy(self) -> None:
        pass

    def __str__(self) -> str:
        return f"GO {type(self).__name__}"


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
    def __init__(self, cell, game_world, player):
        super().__init__(cell, game_world, player)


class Castle(Building):
    hp = 100

    def __init__(self, cell, game_world, player):
        super().__init__(cell, game_world, player)

    def on_destroy(self):
        return super().on_destroy()


class Bank(Building, Iterable):
    hp = 30
    coins_per_iter = 20

    def __init__(self, cell, game_world, player):
        super().__init__(cell, game_world, player)

    def on_iter(self):
        self.player.stats.coins += self.coins_per_iter


class Warriors(GameObject):
    max_distance = 2

    def __init__(self, cell: Cell, game_world: GameWorld, player: Player, count: int):
        super().__init__(cell, game_world, player)
        self.count = count

    def _move(self, target: Position):
        self.game_world.clean_cell(self.cell.position)

        target_object = self.game_world.get_object_by_position(target)
        if target_object is None:
            self.game_world.set_object_to_cell(target, self)
        elif target_object.player == self.player:
            raise IncorrectMovementPositionException
        elif isinstance(target_object, Vulnerable):
            target_object: Vulnerable
            damage = 0
            if target_object.hp >= self.count:
                damage = self.count
            elif target_object.hp < self.count:
                damage = target_object.hp

            target_is_destroyed = target_object.set_damage(damage)
            self.count -= damage

            if self.count <= 0:
                self.game_world.destroy(self)
            elif target_is_destroyed:
                self.game_world.set_object_to_cell(target, self)
        else:
            raise IncorrectMovementPositionException

    def move(self, target: Position) -> bool:
        if (self.game_world.distance(self.cell.position, target) > 2):
            raise IncorrectMovementPositionException
        self._move(target)
        return True


class Stats:
    coins: int = 1000


class Player:
    def __init__(self, team_tag: int):
        self.team_tag = team_tag
        self.stats = Stats()


class GameStates(Enum):
    INIT = 1
    RUN = 2
    COMPLETE = 3


class Game:
    width = 5
    height = 5
    warriors_max_move_distance = 2

    def __init__(self, user_id1, user_id2):
        self.game_state = GameStates.INIT
        self.game_world: GameWorld = GameWorld(self.width, self.height)
        self.user_id_to_team_tag: dict[int, int] = {
            user_id1: 1,
            user_id2: 2
        }
        self.team_tag_to_player = {
            1: Player(1),
            2: Player(2)
        }
        self.go_factory = GameObjectFabric(self.game_world, self.team_tag_to_player)

    def create_users_castle(self):
        x = int(self.width / 2)
        self.go_factory.create_castle(Position(x, 0), 1)
        self.go_factory.create_castle(Position(x, self.height - 1), 2)
        self.game_state = GameStates.RUN

    def move_warriors(self, move_from:Position, move_to:Position, team_tag: int):
        if (not isinstance(self.game_world.get_object_by_position(move_from), Warriors)):
            raise StartCellMustContainWarriorsException 
        warriors: Warriors = self.game_world.get_object_by_position(move_from)
        if  warriors.player.team_tag != team_tag:
            raise GameObjectPermissionDeniedException
        if not warriors.move(move_to):
            raise IncorrectMovementPositionException

    def build_bank(self, position: Position, team_tag: int):
        self.go_factory.create_bank(position, team_tag)

    def buy_warriors(self, position: Position, count: int, team_tag: int):
        game_object = self.game_world.get_object_by_position(position)
        if isinstance(game_object, Warriors):
            game_object.count += count
        else:
            self.go_factory.create_warriors(position, team_tag, count)

    def _iterate_game_loop(self):
        for x in range(self.width):
            for y in range(self.height):
                game_object: GameObject = self.game_world.cells[x][y].game_object
                if isinstance(game_object, Iterable):
                    game_object.on_iter()

    def _process_command(self, command_name:str, command: dict):
        raise IncorrectMovementPositionException
        user_id = command["user_id"]
        if user_id is None or user_id not in list(self.user_id_to_team_tag.keys()):
            raise UnregisteredUserIdException
        
        user_tag = self.user_id_to_team_tag[user_id]
        print("user_tag " + str(user_tag))
        match command_name:
            case "MOVE_WARRIORS":
                mw_command: MoveWarriorsCommand = command
                move_from = Position(**mw_command["move_from"])
                move_to = Position(**mw_command["move_to"])
                self.move_warriors(move_from, move_to, user_tag)
            case "BUILD_BANK":
                build_bank_command: BuildBank = command
                position = Position(**build_bank_command["position"])
                self.build_bank(position, user_tag)
            case "BUY_WARRIORS":
                buy_command: BuyWarriorsCommand = command
                self.buy_warriors(Position(**buy_command["position"]), buy_command["count"], user_tag)
            case _:
                raise CommandNotFound
            
    def _check_game_state(self):
        if self.game_state == GameStates.RUN:
            castles = self.game_world.find_objects_by_type(Castle)
            if len(castles) == 1:
                self.game_state = GameStates.COMPLETE


    def game_step(self, command_name:str, command: dict):
        try:
            self._process_command(command_name, command)
        except GameException as g:
            print(g)
        else:
            self._iterate_game_loop()
            self._check_game_state()
            if self.game_state == GameStates.COMPLETE:
                winner: Player = self.get_winner()
                print("Winner: " + winner.team_tag)

    def get_winner(self) -> None | Player:
        castles = self.game_world.find_objects_by_type(Castle)
        if len(castles) == 0 or len(castles) == 2:
            return None

        if len(castles) == 1:
            self.game_state = GameStates.INIT
            winner_castle: Castle = castles[0]
            return winner_castle.player


user_id1 = 1234
user_id2 = 5678
game = Game(user_id1, user_id2)
game.create_users_castle()
# game.game_step("BUILD_BANK", {"position":{"x":0, "y":0}, "user_id": user_id2})
game.game_step("BUY_WARRIORS", {"position":{"x":2, "y":3}, "count":100, "user_id": user_id1})
game.game_step("MOVE_WARRIORS", {"move_from":{"x": 2, "y": 3}, "move_to":{"x":2, "y":4}, "user_id": user_id1})

game.game_world.print_cells()

# castles = game.game_world.find_objects_by_type(Castle)
# print(castles)



player1 = game.team_tag_to_player[1]
player2 = game.team_tag_to_player[2]
print("user 1: " + str(player1.stats.coins))
print("user 2: " + str(player2.stats.coins))


# gw = GameWorld(3, 3)
# gf = GameObjectFabric(gw, {1: Player(1), 2:Player(2)})

# print(isinstance(gf.create_castle(Position(1,1), 1), Vulnerable))