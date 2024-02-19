from enum import Enum, auto
import random


class ShipSize(Enum):
    CARRIER = 5
    BATTLESHIP = 4
    SUBMARINE = 3
    DESTROYER = 2


class ShipRotation(Enum):
    UP = 3
    DOWN = 2
    LEFT = 1
    RIGHT = 0


class Ship:

    def __init__(self, name, size: ShipSize):
        self.name = name
        self.size = size
        self.rotation = None
        self.start_x = None
        self.start_y = None

    def set_rotation(self, rotation: ShipRotation):
        self.rotation = rotation

    def set_nose_location(self, x, y):
        self.start_x = x
        self.start_y = y


class Player:

    def __init__(self):
        self.shots = 0
        self.ships = {}

    def set_ships(self, s):
        self.ships = s

    def place_ships(self):
        return self.ships


class BattleShipException(Exception):
    pass


class TileState(Enum):
    EMPTY = " "
    EMPTY_MISS = "."
    BOAT_HIT = "x"
    CARRIER = "C"
    BATTLESHIP = "B"
    SUBMARINE1 = "S"
    SUBMARINE2 = "s"
    DESTROYER = "D"


class BattleShip:
    def __init__(self):
        self.current_player_turn = 0
        self._board = [
            [[TileState.EMPTY for _ in range(10)] for _ in range(10)],
            [[TileState.EMPTY for _ in range(10)] for _ in range(10)]
        ]
        self.players = None

    def add_players(self, p1, p2):
        self.players = [p1, p2]

    def validate_and_place_ships(self):
        p0_good = False
        p1_good = False
        p0_ships = self.players[0].place_ships()
        if self._validate_ships(p0_ships):
            if self.place_ships(p0_ships, 0):
                p0_good = True
                print("p0_good")
            else:
                raise BattleShipException("Bad ship placements")
        else:
            raise BattleShipException("Bad ship format data")

        p1_ships = self.players[1].place_ships()
        if self._validate_ships(p1_ships):
            if self.place_ships(p1_ships, 1):
                p1_good = True
                print("p1_good")
            else:
                raise BattleShipException("Bad ship placements")
        else:
            raise BattleShipException("Bad ship format data")
        if p1_good and p0_good:
            return True

    def place_ships(self, ship_dict, player_number):
        boats = {5: 1, 4: 1, 3: 2, 2: 1}
        for type_of_boat in boats.keys():
            type_of_boat = int(type_of_boat)
            for specific in range(boats[type_of_boat]):
                x = ship_dict[type_of_boat][specific]['x']
                y = ship_dict[type_of_boat][specific]['y']
                rot = ship_dict[type_of_boat][specific]['rotation']
                if rot == ShipRotation.DOWN:
                    for _ in range(type_of_boat):
                        if x < 0 or x >= 10 or y < 0 or y >= 10:
                            return False
                        if self._board[player_number][x][y] == TileState.EMPTY:
                            if type_of_boat == 5:
                                self._board[player_number][x][y] = TileState.CARRIER
                            if type_of_boat == 4:
                                self._board[player_number][x][y] = TileState.BATTLESHIP
                            if type_of_boat == 3:
                                if specific == 0:
                                    self._board[player_number][x][y] = TileState.SUBMARINE1
                                if specific == 1:
                                    self._board[player_number][x][y] = TileState.SUBMARINE2
                            if type_of_boat == 2:
                                self._board[player_number][x][y] = TileState.DESTROYER
                        else:
                            return False
                        y += 1
                if rot == ShipRotation.UP:
                    for _ in range(type_of_boat):
                        if x < 0 or x >= 10 or y < 0 or y >= 10:
                            return False
                        if self._board[player_number][x][y] == TileState.EMPTY:
                            if type_of_boat == 5:
                                self._board[player_number][x][y] = TileState.CARRIER
                            if type_of_boat == 4:
                                self._board[player_number][x][y] = TileState.BATTLESHIP
                            if type_of_boat == 3:
                                if specific == 0:
                                    self._board[player_number][x][y] = TileState.SUBMARINE1
                                if specific == 1:
                                    self._board[player_number][x][y] = TileState.SUBMARINE2
                            if type_of_boat == 2:
                                self._board[player_number][x][y] = TileState.DESTROYER
                        else:
                            return False
                        y -= 1
                if rot == ShipRotation.LEFT:
                    for _ in range(type_of_boat):
                        if x < 0 or x >= 10 or y < 0 or y >= 10:
                            return False
                        if self._board[player_number][x][y] == TileState.EMPTY:
                            if type_of_boat == 5:
                                self._board[player_number][x][y] = TileState.CARRIER
                            if type_of_boat == 4:
                                self._board[player_number][x][y] = TileState.BATTLESHIP
                            if type_of_boat == 3:
                                if specific == 0:
                                    self._board[player_number][x][y] = TileState.SUBMARINE1
                                if specific == 1:
                                    self._board[player_number][x][y] = TileState.SUBMARINE2
                            if type_of_boat == 2:
                                self._board[player_number][x][y] = TileState.DESTROYER
                        else:
                            return False
                        x -= 1
                if rot == ShipRotation.RIGHT:
                    for _ in range(type_of_boat):
                        if x < 0 or x >= 10 or y < 0 or y >= 10:
                            return False
                        if self._board[player_number][x][y] == TileState.EMPTY:
                            if type_of_boat == 5:
                                self._board[player_number][x][y] = TileState.CARRIER
                            if type_of_boat == 4:
                                self._board[player_number][x][y] = TileState.BATTLESHIP
                            if type_of_boat == 3:
                                if specific == 0:
                                    self._board[player_number][x][y] = TileState.SUBMARINE1
                                if specific == 1:
                                    self._board[player_number][x][y] = TileState.SUBMARINE2
                            if type_of_boat == 2:
                                self._board[player_number][x][y] = TileState.DESTROYER
                        else:
                            return False
                        x += 1
        return True

    def print_board(self, p):
        print("*"*12)
        for j in range(10):
            row = "*"
            for k in range(10):
                if self._board[p][k][j] == TileState.EMPTY:
                    row += " "
                if self._board[p][k][j] == TileState.EMPTY_MISS:
                    row += "."
                if self._board[p][k][j] == TileState.BOAT_HIT:
                    row += "X"
                if self._board[p][k][j] == TileState.CARRIER:
                    row += "C"
                if self._board[p][k][j] == TileState.BATTLESHIP:
                    row += "B"
                if self._board[p][k][j] == TileState.SUBMARINE1:
                    row += "S"
                if self._board[p][k][j] == TileState.SUBMARINE2:
                    row += "s"
                if self._board[p][k][j] == TileState.DESTROYER:
                    row += "D"
            row+="*"
            print(row)
        print("*"*12)

    def _validate_ships(self, ship_dict):
        ship_keys = {'x', 'y', 'rotation'}
        #
        # "Oh my god, there's a better way. Uncle bob is rolling in his grave." - Fleshy upon viewing this code
        #
        # Overall scheme
        if isinstance(ship_dict, dict):
            if list(ship_dict.keys()) == [5, 4, 3, 2]:
                # carrier
                if len(ship_dict[5]) == 1:
                    if set(ship_dict[5][0].keys()) == ship_keys:
                        if isinstance(ship_dict[5][0]['x'], int) and 0 <= ship_dict[5][0]['x'] <= 9:
                            if isinstance(ship_dict[5][0]['y'], int) and 0 <= ship_dict[5][0]['y'] <= 9:
                                if isinstance(ship_dict[5][0]['rotation'], ShipRotation):
                                    # battleship
                                    if len(ship_dict[4]) == 1:
                                        if set(ship_dict[4][0].keys()) == ship_keys:
                                            if isinstance(ship_dict[4][0]['x'], int) and 0 <= ship_dict[4][0]['x'] <= 9:
                                                if isinstance(ship_dict[4][0]['y'], int) and 0 <= ship_dict[4][0][
                                                    'y'] <= 9:
                                                    if isinstance(ship_dict[4][0]['rotation'], ShipRotation):
                                                        if len(ship_dict[3]) == 2:
                                                            if set(ship_dict[3][0].keys()) == ship_keys and set(
                                                                    ship_dict[3][1].keys()) == ship_keys:
                                                                # submarines
                                                                if isinstance(ship_dict[3][0]['x'], int) and 0 <= \
                                                                        ship_dict[3][0]['x'] <= 9:
                                                                    if isinstance(ship_dict[3][0]['y'], int) and 0 <= \
                                                                            ship_dict[3][0]['y'] <= 9:
                                                                        if isinstance(ship_dict[3][0]['rotation'],
                                                                                      ShipRotation):
                                                                            if isinstance(ship_dict[3][1]['x'],
                                                                                          int) and 0 <= ship_dict[3][1][
                                                                                'x'] <= 9:
                                                                                if isinstance(ship_dict[3][1]['y'],
                                                                                              int) and 0 <= \
                                                                                        ship_dict[3][1]['y'] <= 9:
                                                                                    if isinstance(
                                                                                            ship_dict[3][1]['rotation'],
                                                                                            ShipRotation):
                                                                                        if len(ship_dict[2]) == 1:
                                                                                            if set(ship_dict[2][
                                                                                                       0].keys()) == ship_keys:
                                                                                                # destroyer
                                                                                                if isinstance(
                                                                                                        ship_dict[2][0][
                                                                                                            'x'],
                                                                                                        int) and 0 <= \
                                                                                                        ship_dict[2][0][
                                                                                                            'x'] <= 9:
                                                                                                    if isinstance(
                                                                                                            ship_dict[
                                                                                                                2][0][
                                                                                                                'y'],
                                                                                                            int) and 0 <= \
                                                                                                            ship_dict[
                                                                                                                2][0][
                                                                                                                'y'] <= 9:
                                                                                                        if isinstance(
                                                                                                                ship_dict[
                                                                                                                    2][
                                                                                                                    0][
                                                                                                                    'rotation'],
                                                                                                                ShipRotation):
                                                                                                            return True
        return False

    def make_move(self, x, y):
        if x < 0 or x >= 10 or y < 0 or y >= 10:
            return "Invalid coordinates."

    def check_game_over(self):
        # @TODO DOUBLE CHECK THIS THIS LOGIC
        """
            EMPTY = " "
            EMPTY_MISS = "."
            BOAT_HIT = "x"
            CARRIER = "C"
            BATTLESHIP = "B"
            SUBMARINE1 = "S"
            SUBMARINE2 = "s"
            DESTROYER = "D"
        """
        pass

    def main(self):
        # place_ships
        #  - validate ship placement
        # loop
        # - give players the boards
        # - player 0 goes shoots at player 1
        # - give players the boards
        # - player 1 goes shoots at player 0
        # - check if game is over if yes, break
        # notify each player of score
        pass


# Example usage:
if __name__ == "__main__":
    b = BattleShip()

    a = Player()
    a.set_ships({
        5: [{
            "x": 9,
            "y": 9,
            "rotation": ShipRotation.LEFT,
        }],
        4: [{
            "x": 1,
            "y": 1,
            "rotation": ShipRotation.DOWN,
        }],
        3: [
            {
                "x": 2,
                "y": 1,
                "rotation": ShipRotation.DOWN,
            },
            {
                "x": 3,
                "y": 1,
                "rotation": ShipRotation.DOWN,
            }
        ],
        2: [{
            "x": 4,
            "y": 1,
            "rotation": ShipRotation.DOWN,
        }]
    })

    f = Player()
    f.set_ships({
        5: [{
            "x": 0,
            "y": 0,
            "rotation": ShipRotation.DOWN,
        }],
        4: [{
            "x": 9,
            "y": 0,
            "rotation": ShipRotation.DOWN,
        }],
        3: [
            {
                "x": 4,
                "y": 4,
                "rotation": ShipRotation.RIGHT,
            },
            {
                "x": 0,
                "y": 9,
                "rotation": ShipRotation.UP,
            }
        ],
        2: [{
            "x": 9,
            "y": 9,
            "rotation": ShipRotation.LEFT,
        }]
    })
    b.add_players(a,f)
    b.validate_and_place_ships()
    b.print_board(1)
