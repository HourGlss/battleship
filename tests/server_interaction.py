import time

import requests

url = "http://127.0.0.1:5000"

# ships = {
#             "CARRIER": [{
#                 "x": 9,
#                 "y": 9,
#                 "rotation": "LEFT"
#             }],
#             "BATTLESHIP": [{
#                 "x": 1,
#                 "y": 1,
#                 "rotation": "DOWN"
#             }],
#             "SUBMARINE": [
#                 {
#                     "x": 2,
#                     "y": 1,
#                     "rotation": "DOWN"
#                 },
#                 {
#                     "x": 3,
#                     "y": 1,
#                     "rotation": "DOWN"
#                 }
#             ],
#             "DESTROYER": [{
#                 "x": 4,
#                 "y": 1,
#                 "rotation": "DOWN"
#             }]
#         }

ships = {
    "CARRIER": [{
        "x": 0,
        "y": 0,
        "rotation": "DOWN",
    }],
    "BATTLESHIP": [{
        "x": 9,
        "y": 0,
        "rotation": "DOWN",
    }],
    "SUBMARINE": [
        {
            "x": 4,
            "y": 4,
            "rotation": "RIGHT",
        },
        {
            "x": 0,
            "y": 9,
            "rotation": "UP",
        }
    ],
    "DESTROYER": [{
        "x": 9,
        "y": 9,
        "rotation": "LEFT",
    }]
}


def register_user(name, number):
    data = {
        "username": name,
        "number": number,
    }
    response = requests.post(f"{url}/register", json=data)
    print(response.json())
    assert response.status_code == 200


def create_players(players):
    gameIDs = []
    for player in players:
        register_user(player, 1000000000 + players.index(player))
        response = requests.post(f"{url}/set_open_to_play", json={"username": f"{player}", "open_to_play": "true"})
        time.sleep(.25)
        if response:
            print(response.json())
            gameIDs.extend([x.split(" ")[4] for x in response.json()["message"].split("\n") if x])
    return gameIDs


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

def attack(room_id, username, x, y):
    data = {
        "username": username,
        "x": x,
        "y": y
    }
    response = requests.post(f"{url}/{room_id}/attack", json=data)
    print(response.json())
    assert response.status_code == 200
    return response.json()


if __name__ == "__main__":
    players = ["testuser", "testuser1", "testuser2", "testuser3", "testuser4", "testuser5"]
    # players = ["testuser", "testuser1"]
    gameIDs = create_players(players)
    print(f"GameIDs:{gameIDs}")
    # for each game if player in the game set the ships
    # Set ships for each player in each game
    for gameID in gameIDs:
        users = requests.get(f"{url}/{gameID}/users").json()["users"]
        for player in users:
            if player in players:  # Check if the player is in the list of players we're considering
                set_ships_for_player(player, gameID, ships)

    for gameID in gameIDs:
        get_status(gameID)

    for gameID in gameIDs:
        users = requests.get(f"{url}/{gameID}/users").json()["users"]
        grid = ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
                (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
                (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
                (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
                (4, 0), (4, 1), (4, 2), (4, 3), (4, 4))
        for index in grid:
            for player in users:
                response = attack(gameID, player, index[0], index[1])
                print(get_status(gameID))
                print(response)

    for gameID in gameIDs:
        get_status(gameID)