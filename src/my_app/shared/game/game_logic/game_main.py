from enum import Enum

import my_app.shared.game.game_logic.command as command
import my_app.shared.game.game_logic.core as core
import my_app.shared.game.game_logic.game_exceptions as ge
import my_app.shared.game.game_logic.game_objects as go


class GameObjectFabric:
    warrior_price = 10
    bank_price = 50

    def __init__(
        self, game_world: core.GameWorld,
        team_tag_to_player: dict[int, core.Player]
    ) -> None:
        self.game_world = game_world
        self.team_tag_to_player = team_tag_to_player

    def create_warriors(self, position: core.Position, team_tag: int, count: int) -> go.Warriors:
        if self.game_world.cells[position.x][position.y].game_object is not None:
            raise ge.PositionIsAlreadyBusyException

        warriors_price = count * self.warrior_price
        player = self.team_tag_to_player[team_tag]
        if warriors_price > player.stats.coins:
            raise ge.NotEnoughCoinsException

        player.stats.coins -= warriors_price
        cell: core.Cell = self.game_world.cells[position.x][position.y]
        cell.game_object = go.Warriors(cell, self.game_world, player, count)
        return cell.game_object

    def create_castle(self, position: core.Position, team_tag: int) -> go.Castle:
        if self.game_world.cells[position.x][position.y].game_object is not None:
            raise ge.PositionIsAlreadyBusyException

        player = self.team_tag_to_player[team_tag]
        cell: core.Cell = self.game_world.cells[position.x][position.y]
        cell.game_object = go.Castle(cell, self.game_world, player)
        return cell.game_object

    def create_bank(self, position: core.Position, team_tag: int) -> go.Bank:
        if self.game_world.cells[position.x][position.y].game_object is not None:
            raise ge.PositionIsAlreadyBusyException

        player = self.team_tag_to_player[team_tag]
        if self.bank_price > player.stats.coins:
            raise ge.NotEnoughCoinsException

        player.stats.coins -= self.bank_price
        cell: core.Cell = self.game_world.cells[position.x][position.y]
        cell.game_object = go.Bank(cell, self.game_world, player)
        return cell.game_object


class GameStates(Enum):
    INIT = 1
    RUN = 2
    COMPLETE = 3
    ERROR = 4


class Game:
    width = 5
    height = 5
    warriors_max_move_distance = 2

    def __init__(self, user_id1: int, user_id2: int, baseStats: core.Stats | None = None) -> None:
        self.game_state = GameStates.INIT.value
        self.user_id_to_team_tag: dict[int, int] = {
            user_id1: 1,
            user_id2: 2
        }

        self.team_tag_to_player = {
            1: core.Player(1, user_id1, baseStats.copy() if baseStats is not None else None),
            2: core.Player(2, user_id2, baseStats.copy() if baseStats is not None else None)
        }

        self.game_world: core.GameWorld = core.GameWorld(
            self.width, self.height, self.team_tag_to_player)
        self.go_factory = GameObjectFabric(self.game_world, self.team_tag_to_player)
        self.whose_step = 1

    def change_whose_turn(self) -> None:
        if self.whose_step == 1:
            self.whose_step = 2
        else:
            self.whose_step = 1

    def is_user_turn(self, user_id: int) -> bool:
        if user_id not in self.user_id_to_team_tag:
            raise ge.UnregisteredUserIdException
        return self.whose_step == self.user_id_to_team_tag[user_id]

    def is_correct_spawn_zone(self, position: core.Position, team_tag: int) -> bool:
        half_height = int(self.height / 2) - 1
        if team_tag == 1:
            if position.y > half_height:
                return False
        else:
            if position.y < (self.height - 1 - half_height):
                return False
        return True

    def create_users_castle(self) -> None:
        x = int(self.width / 2)
        self.go_factory.create_castle(core.Position(x, 0), 1)
        self.go_factory.create_castle(core.Position(x, self.height - 1), 2)
        self.game_state = GameStates.RUN.value

    def move_warriors(
        self, move_from: core.Position,
        move_to: core.Position,
        team_tag: int
    ) -> None:
        if (not isinstance(self.game_world.get_object_by_position(move_from), go.Warriors)):
            raise ge.StartCellMustContainWarriorsException
        warriors: go.Warriors = self.game_world.get_object_by_position(move_from)
        if warriors.player.team_tag != team_tag:
            raise ge.GameObjectPermissionDeniedException
        warriors.move(move_to)

    def build_bank(self, position: core.Position, team_tag: int) -> None:
        if not self.is_correct_spawn_zone(position, team_tag):
            raise ge.IncorrectZone
        self.go_factory.create_bank(position, team_tag)

    def buy_warriors(self, position: core.Position, count: int, team_tag: int) -> None:
        if not self.is_correct_spawn_zone(position, team_tag):
            raise ge.IncorrectZone
        game_object = self.game_world.get_object_by_position(position)
        if isinstance(game_object, go.Warriors):
            game_object.count += count
        else:
            self.go_factory.create_warriors(position, team_tag, count)

    def _iterate_game_loop(self) -> None:
        for x in range(self.width):
            for y in range(self.height):
                game_object: go.GameObject = self.game_world.cells[x][y].game_object
                if isinstance(game_object, go.Iterable):
                    game_object.on_iter()

    def _process_command(self, income_command: command.GameCommand) -> None:
        user_id = income_command["user_id"]
        if user_id is None or user_id not in list(self.user_id_to_team_tag.keys()):
            raise ge.UnregisteredUserIdException

        user_tag = self.user_id_to_team_tag[user_id]
        if user_tag != self.whose_step:
            raise ge.NotYourStep
        command_name = income_command["command_name"]
        match command_name:
            case "MOVE_WARRIORS":
                mw_command: command.MoveWarriorsCommand = income_command
                move_from = core.Position(**mw_command["move_from"])
                move_to = core.Position(**mw_command["move_to"])
                self.move_warriors(move_from, move_to, user_tag)
            case "BUILD_BANK":
                build_bank_command: command.BuildBankCommand = income_command
                position = core.Position(**build_bank_command["position"])
                self.build_bank(position, user_tag)
            case "BUY_WARRIORS":
                buy_command: command.BuyWarriorsCommand = income_command
                self.buy_warriors(core.Position(
                    **buy_command["position"]), buy_command["count"], user_tag)
            case _:
                raise ge.CommandNotFound

    def _check_game_state(self) -> None:
        if self.game_state == GameStates.ERROR.value:
            self.game_state = GameStates.RUN.value
        if self.game_state == GameStates.RUN.value:
            castles = self.game_world.find_objects_by_type(go.Castle)
            if len(castles) == 1:
                self.game_state = GameStates.COMPLETE.value

    def game_step(self, command: command.GameCommand) -> int:
        try:
            self._process_command(command)
        except ge.GameException as game_exception:
            self.game_state = GameStates.ERROR.value
            raise game_exception
        else:
            self._iterate_game_loop()
            self._check_game_state()
            self.change_whose_turn()

        return self.game_state

    def get_winner(self) -> None | core.Player:
        castles = self.game_world.find_objects_by_type(go.Castle)
        if len(castles) == 0 or len(castles) == 2:
            return None

        if len(castles) == 1:
            self.game_state = GameStates.INIT.value
            winner_castle: go.Castle = castles[0]
            return winner_castle.player
        return None


if __name__ == "__main__":
    user_id1 = 1234
    user_id2 = 5678
    game = Game(user_id1, user_id2)
    game.create_users_castle()

    game.game_step({"command_name": "BUY_WARRIORS",
                    "position":  {"x": 1, "y": 1}, "user_id": user_id1, "count": 10})
    game.game_step({"command_name": "BUY_WARRIORS",
                    "position": {"x": 1, "y": 3}, "user_id": user_id2, "count": 10})
    game.game_step({"command_name": "MOVE_WARRIORS",
                    "move_from":  {"x": 1, "y": 1},
                    "move_to": {"x": 1, "y": 3}, "user_id": user_id1})

    game.game_world.print_cells()
    player1 = game.team_tag_to_player[1]
    player2 = game.team_tag_to_player[2]
    print("user 1: " + str(player1.stats.coins))
    print("user 2: " + str(player2.stats.coins))
