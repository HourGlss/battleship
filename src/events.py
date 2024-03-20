import secrets
import string
import socket
import time
import base64

from flask import request
from itertools import combinations
from Crypto.Random import get_random_bytes

from .extensions import socketio, secure_server
from .game_controller import GameController
from .pocs.crypto_example_1 import cipher_aes
from .shared_state import players, connections, rooms, threads


def generate_room_id(length=8):
    # Generate a secure random string of specified length
    alphabet = string.ascii_letters + string.digits
    room_id = ''.join(secrets.choice(alphabet) for i in range(length))
    return room_id


def find_playerid_by_username(username):
    for playerid, info in players.items():
        if info['username'] == username:
            return playerid
    return None


def find_open_windows_port():
    # Create a new socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind to an address with port 0, letting the OS pick an available port
        s.bind(('', 0))
        # Get the port number assigned by the OS
        port = s.getsockname()[1]
        # Return the open port number
        return port


def remove_room(room_id):
    del rooms[room_id]
    del threads[room_id]


def exchange_keys(clientid):
    enc_session_key, cipher_aes.nonce, tag, ciphertext = secure_server.initial_send(players[clientid]["username"],
                                                                                    players[clientid]["rec_key"])
    socketio.emit("initial send", {"enc_session_key": enc_session_key,
                                   "cipher_aes.nonce": cipher_aes.nonce,
                                   "tag": tag, "ciphertext": ciphertext
                                   }, to=players[clientid]["sid"])
    players[clientid]["last_heard"] = time.time()
    socketio.emit("response", {"message": "connected to server"}, to=players[clientid]["sid"])


@socketio.on("connect")
def connect(auth):
    clientid = get_random_bytes(16)
    username = request.headers.get("username")
    rec_key = base64.urlsafe_b64decode(auth.get("rec_key").encode("utf-8"))
    players[clientid] = {"username": username, "last_heard": time.time(), "open_to_play": False, "sid": request.sid,
                         "rec_key": rec_key}


@socketio.on("initial send")
def handle_initial_send(data):
    exchange_keys(find_playerid_by_username(data["username"]))


@socketio.on("register")
def handle_register(data):
    recv = secure_server.receive_data(data["username"], data["payload"])
    if recv == "Registering":
        print("Registering player", data)
        players[request.sid] = {"username": data["username"], "last_heard": time.time()}
        players[request.sid]["open_to_play"] = False
    else:
        print("unauthorized access attempt")


@socketio.on('disconnect')
def handle_disconnect():
    """
    May need some additional logic to handle disconnections
    :return:
    """
    # Remove the player from the dictionary upon disconnection
    player_sid = request.sid  # The session ID of the client
    if player_sid in players.values():
        player_id = [key for key, value in players.items() if value == player_sid][0]
        del players[player_id]
        print(f"Player {player_id} has been disconnected and removed.")


@socketio.on("message")
def handle_message(data):
    recv = secure_server.receive_data(data["username"], data["payload"])
    print("Message from client: ", recv)
    message = secure_server.send_data(data["username"], "Message received")
    socketio.emit("response", {"message": message})


@socketio.on("ping")
def handle_ping(data):
    recv = secure_server.receive_data(data["username"], data["payload"])
    print(f"Ping from client: {data['username']}", recv)
    socketio.emit("heartbeat", room=request.sid)


@socketio.on('heartbeat_response')
def handle_heartbeat_response(data):
    print(f"Received heartbeat response from {data['username']}")
    player_id = find_playerid_by_username(data['username'])
    if player_id in players.keys():
        print(f"Updating last_heard for player {player_id}")
        # Update the 'last_heard' timestamp for the responding player
        players[player_id]['last_heard'] = time.time()


@socketio.on('open_to_play')
def set_open_to_play(data):
    payload_tuple = (data["payload"]["tag"], data["payload"]["nonce"], data["payload"]["ciphertext"])
    recv = secure_server.receive_data(data["username"], payload_tuple)
    if recv == "Open to play":
        players[find_playerid_by_username(data["username"])]["open_to_play"] = True
        print("Open to play")
        # Get all unique combinations of players of length 2

        # filter out players who are not open to play or do not have key 'open_to_play'
        players_list = []
        for player in players.keys():
            if players[player].get("open_to_play"):
                print(players[player]["username"])
                players_list.append(player)
        print(players_list)
        comb = combinations(players_list, 2)

        # Convert combinations to a list once so we can iterate multiple times
        all_combinations = list(comb)

        # Ensure to use the already converted list 'all_combinations'
        for i in all_combinations:
            p1_name = players[i[0]]["username"]
            p2_name = players[i[1]]["username"]

            if f"{i[0]}+{i[1]}" not in rooms.values():
                room_id = generate_room_id()

                thread = GameController(find_open_windows_port(), room_id, remove_room)
                # Use the sids instead of usernames when adding players
                thread.add_player(players[i[0]]["username"], players[i[0]]["sid"])
                thread.add_player(players[i[1]]["username"], players[i[1]]["sid"])
                # Assuming get_port() is meant to retrieve and print or use the port in some way
                # TODO
                socketio.emit("get_port", {"port": thread.port}, to=players[i[0]]["sid"])
                socketio.emit("get_port", {"port": thread.port}, to=players[i[1]]["sid"])

                # thread.get_port()  # Store or use the port if necessary
                rooms[room_id] = f"{i[0]}+{i[1]}"
                threads[room_id] = {"players": (p1_name, p2_name), "game_controller": thread}
                thread.start()


@socketio.event
def poll_connections():
    for key, value in players.items():
        socketio.emit("poll", room=key)
