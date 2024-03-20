from .utils import TileState, BattleShipException, ShipRotation


class Player:

    def __init__(self):
        self.shots = 0
        self.ships = {}

    def set_ships(self, s):
        self.ships = s

    def place_ships(self):
        return self.ships


class Battleship:
    def __init__(self):
        self.current_player_turn = None
        self._board = [
            [[TileState.EMPTY for _ in range(10)] for _ in range(10)],
            [[TileState.EMPTY for _ in range(10)] for _ in range(10)]
        ]
        self.players = None
        self.boats_placed = False

    def add_players(self, p1, p2):
        self.players = [p1, p2]

    def has_player(self, player):
        if self.players is None:
            return False
        return player in self.players

    def validate_and_place_ships(self):
        p0_good = False
        p1_good = False
        p0_ships = self.players[0].place_ships()
        if self._validate_ships(p0_ships):
            if self._place_ships(p0_ships, 0):
                p0_good = True
                # print("p0_good")
            else:
                raise BattleShipException("Bad ship placements")
        else:
            raise BattleShipException("Bad ship format data")

        p1_ships = self.players[1].place_ships()
        if self._validate_ships(p1_ships):
            if self._place_ships(p1_ships, 1):
                p1_good = True
                # print("p1_good")
            else:
                raise BattleShipException("Bad ship placements")
        else:
            raise BattleShipException("Bad ship format data")
        if p1_good and p0_good:
            self.boats_placed = True
            self.current_player_turn = 0
            return True
        else:
            raise BattleShipException("How did I get here?")

    def _place_ships(self, ship_dict, player_number):
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

    def print_my_board(self, p):
        board = ("*" * 12) + "\n"
        for j in range(10):
            board += "*"
            for k in range(10):
                board += self._board[p][k][j].value  # Directly use the value for the player's own board
            board += "*" + "\n"
        board += "*" * 12
        print(board)
        return board

    def print_opponent_board(self, p):
        board = ("*" * 12) + "\n"
        for j in range(10):
            board += "*"
            for k in range(10):
                # For the opponent's board, filter out the ship locations
                value = self._board[p][k][j].value
                if value in ["S", "s", "B", "D", "C"]:  # If it's a ship, just show empty sea unless it's been hit
                    board += ' '
                else:
                    board += value  # Show hits and misses as they are
            board += "*" + "\n"
        board += "*" * 12
        print(board)
        return board

    def make_move(self, p, x, y):
        """
        0 = MISS , _
        1 = HIT , _
        2 = KILL, TYPE_of_BOAT (5 = carrier, 4 = battleship, 3 = sub1, 2 = sub2, 1 = destroyer)
        :param p: attacking player int
        :param x: coord
        :param y: coord
        :return:
        """
        if x < 0 or x >= 10 or y < 0 or y >= 10:
            raise BattleShipException("Invalid coordinates.")
        target = None
        if p == 0:
            target = 1
        elif p == 1:
            target = 0
        result = None
        self.current_player_turn = target

        current = [0, 0, 0, 0, 0]
        after = [0, 0, 0, 0, 0]
        for j in range(10):
            for k in range(10):
                if self._board[target][j][k] == TileState.CARRIER:
                    current[4] += 1
                if self._board[target][j][k] == TileState.BATTLESHIP:
                    current[3] += 1
                if self._board[target][j][k] == TileState.SUBMARINE2:
                    current[2] += 1
                if self._board[target][j][k] == TileState.SUBMARINE1:
                    current[1] += 1
                if self._board[target][j][k] == TileState.DESTROYER:
                    current[0] += 1
        # print(f"c {current}", end = " ")
        ct = self._board[target][x][y]
        if (
                ct == TileState.CARRIER or
                ct == TileState.BATTLESHIP or
                ct == TileState.DESTROYER or
                ct == TileState.SUBMARINE1 or
                ct == TileState.SUBMARINE2 or
                ct == TileState.BOAT_HIT
        ):
            self._board[target][x][y] = TileState.BOAT_HIT
            result = 1, 0
        elif (
                ct == TileState.EMPTY or
                ct == TileState.EMPTY_MISS
        ):
            self._board[target][x][y] = TileState.EMPTY_MISS
            result = 0, 0
        for j in range(10):
            for k in range(10):
                if self._board[target][j][k] == TileState.CARRIER:
                    after[4] += 1
                if self._board[target][j][k] == TileState.BATTLESHIP:
                    after[3] += 1
                if self._board[target][j][k] == TileState.SUBMARINE2:
                    after[2] += 1
                if self._board[target][j][k] == TileState.SUBMARINE1:
                    after[1] += 1
                if self._board[target][j][k] == TileState.DESTROYER:
                    after[0] += 1
        # print(f"after {after}",end = " ")
        for i, _ in enumerate(current):
            if _ != 0:
                if _ != after[i] and after[i] == 0:
                    result = 2, i
                    # print("YES", end= " ")
                    break
        # print(result)
        return result

    def check_game_over(self):
        # p0 check
        p0_alive = False
        for j in range(10):
            for k in range(10):
                ct = self._board[0][j][k]
                if ct == TileState.EMPTY or ct == TileState.EMPTY_MISS or ct == TileState.BOAT_HIT:
                    continue
                else:
                    p0_alive = True
                    break
            if p0_alive:
                break
        # p1 check
        p1_alive = False
        for j in range(10):
            for k in range(10):
                ct = self._board[1][j][k]
                if ct == TileState.EMPTY or ct == TileState.EMPTY_MISS or ct == TileState.BOAT_HIT:
                    continue
                else:
                    p1_alive = True
                    break
            if p1_alive:
                break
        return p0_alive, p1_alive

    def get_status(self):
        p0_alive, p1_alive = self.check_game_over()
        return {
            "placed": self.boats_placed,
            "cplayer": self.current_player_turn,
            "p0_alive": p0_alive,
            "p1_alive": p1_alive,
        }

    def _validate_ships(self, ship_dict):
        print("Ship_dict: ", ship_dict)
        ship_keys = {'x', 'y', 'rotation'}
        if not isinstance(ship_dict, dict):
            print(1)
            return False
        if set(ship_dict.keys()) != {2, 3, 4, 5}:
            print(2)
            print(ship_dict.keys())
            return False
        if len(ship_dict[3]) != 2:
            print(3)
            return False
        for size in ship_dict.keys():
            ships = ship_dict[size]
            for ship in ships:
                if not isinstance(ship, dict) or set(ship.keys()) != ship_keys:
                    print(4)
                    return False
                if not all(isinstance(ship[key], int) and 0 <= ship[key] <= 9 for key in ['x', 'y']):
                    print(5)
                    return False
                if not isinstance(ship['rotation'], ShipRotation):
                    print(6)
                    return False
        return True


# Example usage:
if __name__ == "__main__":
    b = Battleship()
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
                "y": 2,
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
                "x": 8,
                "y": 0,
                "rotation": ShipRotation.DOWN,
            },
            {
                "x": 7,
                "y": 0,
                "rotation": ShipRotation.DOWN,
            }
        ],
        2: [{
            "x": 6,
            "y": 0,
            "rotation": ShipRotation.DOWN,
        }]
    })
    b.add_players(a, f)
    b.validate_and_place_ships()
    b.print_board(1)
    b.make_move(0, 0, 6)
    # carrier
    b.make_move(0, 0, 0)
    b.make_move(0, 0, 1)
    b.make_move(0, 0, 2)
    b.make_move(0, 0, 3)
    b.make_move(0, 0, 4)
    # battleship
    b.make_move(0, 9, 0)
    b.make_move(0, 9, 1)
    b.make_move(0, 9, 2)
    b.make_move(0, 9, 3)
    # sub1
    b.make_move(0, 0, 9)
    b.make_move(0, 0, 8)
    b.make_move(0, 0, 7)
    # sub2
    b.make_move(0, 4, 4)
    b.make_move(0, 5, 4)
    b.make_move(0, 6, 4)
    # destroyer
    b.make_move(0, 8, 9)
    b.make_move(0, 9, 9)
    #
    # b.print_board(1)
    # print(b.check_game_over())
