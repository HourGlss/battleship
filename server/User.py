from enum import Enum
from typing import TypedDict, List, Dict


class ShipRotation(Enum):
    UP = 3
    DOWN = 2
    LEFT = 1
    RIGHT = 0


class ShipPosition(TypedDict):
    x: int
    y: int
    rotation: ShipRotation


class ShipSize(Enum):
    CARRIER = 5
    BATTLESHIP = 4
    SUBMARINE = 3
    DESTROYER = 2


class ShipsConfig(TypedDict, total=False):  # 'total=False' allows missing keys
    CARRIER: List[ShipPosition]
    BATTLESHIP: List[ShipPosition]
    SUBMARINE: List[ShipPosition]
    DESTROYER: List[ShipPosition]


class User:
    def __init__(self, name, number, public_key):
        self.name = name
        self.number = number
        self.public_key = public_key
        self.open_to_play = "false"
        self.ships: Dict[ShipSize, List[ShipPosition]] = {
            ShipSize.CARRIER: [],
            ShipSize.BATTLESHIP: [],
            ShipSize.SUBMARINE: [],
            ShipSize.DESTROYER: []
        }

    def __str__(self):
        return f"{self.name} "

    def set_open_to_play(self, open_to_play):
        self.open_to_play = open_to_play

    def set_ships(self, ships):
        self.ships = ships
