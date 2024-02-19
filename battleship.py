from enum import Enum, auto
import random


class BoardStates(Enum):
    SETUP = 0
    OVER = 3
    PLAYER_ONE = 1
    PLAYER_TWO = 2


class TileState(Enum):
    EMPTY = " "
    BOAT = "b"
    EMPTY_MISS = "."
    BOAT_HIT = "x"

class ShipSize(Enum):
    CARRIER = 5
    BATTLESHIP = 4
    CRUISER = 3
    BOAT_HIT = "x"

class Ship:

    def __init__(self, size, rotation, x, y):
        self.size = size
        self.rotation = rotation
        self.start_x = x
        self.start_y = y


class BattleShip:
    def __init__(self):
        self.state = BoardStates.SETUP
        self.turn = 0
        self.num_turns = 0
        self.board = [
            [[TileState.EMPTY for _ in range(10)] for _ in range(10)],
            [[TileState.EMPTY for _ in range(10)] for _ in range(10)]
        ]

    def place_ship(self, player, x, y, ship: Ship):
        # @TODO MAKE THIS MORE THAN ONE SPOT
        if self.state != BoardStates.SETUP:
            return "Cannot place ships once the game has started."

        if x < 0 or x >= 10 or y < 0 or y >= 10:
            return "Invalid coordinates."

        if self.board[player][x][y] != TileState.EMPTY:
            return "Cannot place a ship here."

        self.board[player][x][y] = TileState.BOAT
        return "Ship placed successfully."

    def make_move(self, player, x, y):
        if self.state != BoardStates.PLAYER_ONE and self.state != BoardStates.PLAYER_TWO:
            return "Game hasn't started yet."

        if x < 0 or x >= 10 or y < 0 or y >= 10:
            return "Invalid coordinates."

        opponent = 1 - player
        if self.board[opponent][x][y] == TileState.BOAT:
            self.board[opponent][x][y] = TileState.BOAT_HIT
            return "Hit!"
        elif self.board[opponent][x][y] == TileState.EMPTY:
            self.board[opponent][x][y] = TileState.EMPTY_MISS
            return "Miss!"
        else:
            return "You've already fired at this position."

    def start_game(self):
        if self.state != BoardStates.SETUP:
            return "Game has already started or is over."

        # Check if ships are placed for both players
        # @TODO DOUBLE CHECK THIS LOGIC
        for player in range(2):
            if any(TileState.BOAT in row for row in self.board[player]):
                self.state = BoardStates.PLAYER_ONE if player == 0 else BoardStates.PLAYER_TWO
                return f"Player {player + 1} turn to start."

        return "Both players need to place ships first."

    def check_game_over(self):
        # @TODO DOUBLE CHECK THIS THIS LOGIC
        for player in range(2):
            if all(cell != TileState.BOAT for row in self.board[1 - player] for cell in row):
                self.state = BoardStates.OVER
                return f"Player {player + 1} wins!"

        return None  # Game is not over yet


# Example usage:
if __name__ == "__main__":
    game = BattleShip()
    print(game.place_ship(0, 3, 4))  # Place a ship for player 1 at coordinates (3, 4)
    print(game.place_ship(1, 5, 6))  # Place a ship for player 2 at coordinates (5, 6)

    print(game.start_game())  # Start the game
    print(game.make_move(0, 5, 6))  # Player 1 makes a move at coordinates (5, 6)
    print(game.make_move(1, 3, 4))  # Player 2 makes a move at coordinates (3, 4)

    print(game.check_game_over())  # Check if the game is over
