from src.utils import ShipRotation

players = {}
connections = []

rooms = {}
threads = {}

test_ship_dict = {
        5: [{
            "x": 9,
            "y": 9,
            "rotation": ShipRotation.LEFT.value,
        }],
        4: [{
            "x": 1,
            "y": 1,
            "rotation": ShipRotation.DOWN.value,
        }],
        3: [
            {
                "x": 2,
                "y": 1,
                "rotation": ShipRotation.DOWN.value,
            },
            {
                "x": 3,
                "y": 2,
                "rotation": ShipRotation.DOWN.value,
            }
        ],
        2: [{
            "x": 4,
            "y": 1,
            "rotation": ShipRotation.DOWN.value,
        }]
    }
