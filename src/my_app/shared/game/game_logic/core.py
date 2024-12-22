from __future__ import annotations

from abc import ABC, abstractmethod


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class Cell:
    def __init__(self, position: Position, game_object: "GameObject" | None = None):
        self.position = position
        self.game_object = game_object


class Stats:
    def __init__(self, coins: int = 20000) -> None:
        self.coins = coins

    def copy(self) -> Stats:
        return Stats(self.coins)


class Player:
    def __init__(self, team_tag: int, user_id: int, stats: Stats | None = None):
        self.user_id = user_id
        self.team_tag = team_tag
        self.stats = Stats() if stats is None else stats


class GameObject(ABC):
    def __init__(self, cell: Cell, game_world: GameWorld, player: Player) -> None:
        self.cell: Cell | None = cell
        self.game_world = game_world
        self.player = player

    @abstractmethod
    def on_destroy(self) -> None:
        pass

    def __str__(self) -> str:
        return f"GO {type(self).__name__}"


class GameWorld:
    def __init__(
        self,
        width: int,
        height: int, player_by_tag: dict[int, Player],
        cells: list[list[Cell]] | None = None
    ):
        self.width = width
        self.height = height
        self.player_by_tag = player_by_tag
        if cells is None:
            self.cells = []
            for x in range(width):
                line_cells = []
                for y in range(height):
                    line_cells.append(Cell(Position(x, y)))
                self.cells.append(line_cells)
        else:
            self.cells = cells

    def distance(self, position1: Position, position2: Position) -> int:
        return abs(position1.x - position2.x) + abs(position1.y - position2.y)

    def get_object_by_position(self, position: Position) -> GameObject | None:
        return self.cells[position.x][position.y].game_object

    def set_object_to_cell(self, position: Position, game_object: GameObject) -> None:
        self.cells[position.x][position.y].game_object = game_object
        game_object.cell = self.cells[position.x][position.y]

    def clean_cell(self, position: Position) -> None:
        cell = self.cells[position.x][position.y]
        if cell.game_object is not None:
            cell.game_object = None
            self.cells[position.x][position.y].game_object = None

    def find_objects_by_type(self, target_type: type) -> list[GameObject]:
        game_objects: list[GameObject] = []
        for x in range(self.width):
            for y in range(self.height):
                game_object = self.get_object_by_position(Position(x, y))
                if isinstance(game_object, target_type) and isinstance(game_object, GameObject):
                    game_objects.append(game_object)

        return game_objects

    def destroy(self, game_object: GameObject) -> None:
        game_object.on_destroy()
        if game_object.cell is None:
            return
        pos = game_object.cell.position
        game_object.cell = None
        self.cells[pos.x][pos.y].game_object = None
        print("Destroy " + type(game_object).__name__)

    def print_cells(self) -> None:
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                cell = self.cells[x][y]
                if cell is None:
                    return
                game_object = cell.game_object
                line += type(game_object).__name__
                if game_object is not None:
                    line += f"({game_object.player.team_tag})"
                line += "  "
            print(line+"\n")
