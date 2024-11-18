from __future__ import annotations
from abc import ABC
import json


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class Cell:
    def __init__(self, position: Position, game_object: "GameObject" | None = None):
        self.position = position
        self.game_object = game_object


class Stats:
    coins: int = 20000


class Player:
    def __init__(self, team_tag: int, user_id: int):
        self.user_id = user_id
        self.team_tag = team_tag
        self.stats = Stats()

class GameObject(ABC):
    def __init__(self, cell: Cell, game_world: GameWorld, player: Player):
        self.cell = cell
        self.game_world = game_world
        self.player = player

    def on_destroy(self) -> None:
        pass

    def __str__(self) -> str:
        return f"GO {type(self).__name__}"


class GameWorld:
    def __init__(self, width: int, height: int, cells:list[list[Cell]] | None = None):
        self.width = width
        self.height = height

        if cells is None:
            self.cells = []
            for x in range(width):
                line_cells = []
                for y in range(height):
                    line_cells.append(Cell(Position(x, y)))
                self.cells.append(line_cells)
        else:
            self.cells = cells

    def distance(self, position1: Position, position2: Position):
        return abs(position1.x - position2.x) + abs(position1.y - position2.y)

    def get_object_by_position(self, position: Position) -> GameObject | None:
        return self.cells[position.x][position.y].game_object

    def set_object_to_cell(self, position: Position, game_object: GameObject):
        self.cells[position.x][position.y].game_object = game_object
        game_object.cell = self.cells[position.x][position.y]

    def clean_cell(self, position: Position):
        cell = self.cells[position.x][position.y]
        if cell.game_object != None:
            cell.game_object = None
            self.cells[position.x][position.y].game_object = None

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
        game_object.cell = None
        self.cells[pos.x][pos.y].game_object = None
        print("Destroy " + type(game_object).__name__)

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