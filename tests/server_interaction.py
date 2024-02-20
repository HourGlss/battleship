import time

import requests

url = "http://127.0.0.1:5000"


def register_user(name, number):
    data = {
        "username": name,
        "number": number,
    }
    response = requests.post(f"{url}/register", json=data)
    print(response.json())
    assert response.status_code == 200


def create_game():
    data = {
        "username": "testuser"
    }
    response = requests.post(f"{url}/hostgame", json=data)
    print(response.json())
    room_id = response.json()["room_id"]
    assert response.status_code == 200
    return room_id


def set_ships_for_player(player, id, ships):
    data = {
        "username": player,
        "ships": ships
    }
    response = requests.post(f"{url}/{id}/set_ships", json=data)
    print(response.json())
    assert response.status_code == 200


def join_game(room_id, username):
    data = {
        "username": username,
        "room_id": room_id
    }
    response = requests.post(f"{url}/{room_id}/join", json=data)
    print(response.json())
    assert response.status_code == 200

def get_status(room_id):
    response = requests.get(f"{url}/{room_id}/get_status")
    print(response.json())
    assert response.status_code == 200
    return response.json()


if __name__ == "__main__":
    register_user("testuser", 1000000000)
    register_user("testuser1", 1000000001)
    gameID = create_game()

    time.sleep(1)
    set_ships_for_player("testuser", gameID, {
        "CARRIER": [{
            "x": 9,
            "y": 9,
            "rotation": "LEFT"
        }],
        "BATTLESHIP": [{
            "x": 1,
            "y": 1,
            "rotation": "DOWN"
        }],
        "SUBMARINE": [
            {
                "x": 2,
                "y": 1,
                "rotation": "DOWN"
            },
            {
                "x": 3,
                "y": 1,
                "rotation": "DOWN"
            }
        ],
        "DESTROYER": [{
            "x": 4,
            "y": 1,
            "rotation": "DOWN"
        }]
    })
    set_ships_for_player("testuser1", gameID, {
        "CARRIER": [{
            "x": 9,
            "y": 9,
            "rotation": "LEFT"
        }],
        "BATTLESHIP": [{
            "x": 1,
            "y": 1,
            "rotation": "DOWN"
        }],
        "SUBMARINE": [
            {
                "x": 2,
                "y": 1,
                "rotation": "DOWN"
            },
            {
                "x": 3,
                "y": 1,
                "rotation": "DOWN"
            }
        ],
        "DESTROYER": [{
            "x": 4,
            "y": 1,
            "rotation": "DOWN"
        }]
    })
    get_status(gameID)

