from enum import Enum
from typing import TypedDict, List


class ShipRotation(Enum):
    LEFT = "LEFT"
    DOWN = "DOWN"

class ShipPosition(TypedDict):
    x: int
    y: int
    rotation: ShipRotation

class ShipsConfig(TypedDict):
    5: List[ShipPosition]
    4: List[ShipPosition]
    3: List[ShipPosition]
    2: List[ShipPosition]

class User:
    def __init__(self, name, number, public_key):
        self.name = name
        self.number = number
        self.public_key = public_key
        self.open_to_play = "false"
        self.ships: dict[int, list[dict[s]]] = {}

    def __str__(self):
        return f"{self.name} "

    def set_open_to_play(self, open_to_play):
        self.open_to_play = open_to_play

    def set_ships(self, ships):
        self.ships = ships