import secrets
import string
import socket
import time

from flask import request
from flask_socketio import join_room, send, leave_room, emit
from itertools import combinations

from .extensions import socketio
import threading
from .game_controller import GameController
from .shared_state import players, connections, rooms, threads


def generate_room_id(length=8):
    # Generate a secure random string of specified length
    alphabet = string.ascii_letters + string.digits
    room_id = ''.join(secrets.choice(alphabet) for i in range(length))
    return room_id

def find_sid_by_username(username):
    for sid, info in players.items():
        if info['username'] == username:
            return sid
    return None



def find_open_port():
    # Create a new socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind to an address with port 0, letting the OS pick an available port
        s.bind(('', 0))
        # Get the port number assigned by the OS
        port = s.getsockname()[1]
        # Return the open port number
        return port


@socketio.on("connect")
def handle_connect():
    print("Client Connected")
    players[request.sid] = {"last_heard": time.time()}
    socketio.emit("response", {"message": "connected to server"}, to=request.sid)


@socketio.on("register")
def handle_register(data):
    print("Registering player", data)
    players[request.sid] = {"username": data["username"], "last_heard": time.time()}
    players[request.sid]["open_to_play"] = False


@socketio.on('disconnect')
def handle_disconnect():
    # Remove the player from the dictionary upon disconnection
    player_id = request.sid  # The session ID of the client
    if player_id in players:
        del players[player_id]
        print(f"Player {player_id} has been disconnected and removed.")


@socketio.on("message")
def handle_message(data):
    print("Message from client: ", data)
    socketio.emit("response", {"from": "server"})


@socketio.on("ping")
def handle_ping(data):
    print("Received ping from", request.sid)
    socketio.emit("heartbeat", {"from": "server"}, room=request.sid)


@socketio.on('heartbeat_response')
def handle_heartbeat_response(data):
    print(f"Received heartbeat response from {request.sid}")
    player_id = request.sid
    if player_id in players:
        print(f"Updating last_heard for player {player_id}")
        # Update the 'last_heard' timestamp for the responding player
        players[player_id]['last_heard'] = time.time()


@socketio.on('open_to_play')
def set_open_to_play():
    players[request.sid]["open_to_play"] = True
    print("Open to play")
    # Get all unique combinations of players of length 2
    print(players.values())

    # filter out players who are not open to play
    players_list = [player for player in players.keys() if players[player]["open_to_play"]]

    comb = combinations(players_list, 2)

    # Convert combinations to a list once so we can iterate multiple times
    all_combinations = list(comb)

    # Ensure to use the already converted list 'all_combinations'
    for i in all_combinations:
        p1_name = players[i[0]]["username"]
        p2_name = players[i[1]]["username"]

        if f"{i[0]}+{i[1]}" not in rooms.values():
            room_id = generate_room_id()
            thread = GameController(find_open_port(), room_id)
            # Use the sids instead of usernames when adding players
            thread.add_player(players[i[0]]["username"], i[0])
            thread.add_player(players[i[1]]["username"], i[1])
            # Assuming get_port() is meant to retrieve and print or use the port in some way
            socketio.emit("get_port", {"port": thread.port}, to=i[0])
            socketio.emit("get_port", {"port": thread.port}, to=i[1])

            thread.get_port()  # Store or use the port if necessary
            rooms[room_id] = f"{i[0]}+{i[1]}"
            threads[room_id] = {"players": (p1_name, p2_name), "game_controller": thread}
            thread.start()


@socketio.event
def poll_connections():
    for key, value in players.items():
        socketio.emit("poll", room=key)
