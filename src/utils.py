from enum import Enum


class ShipRotation(Enum):
    UP = 3
    DOWN = 2
    LEFT = 1
    RIGHT = 0


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
