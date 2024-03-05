from flask import request, jsonify, render_template
from battleship import socketio
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from User import User
from Battleship.server.Manager import Manager
from Battleship.server.Room import Room
from utils import ShipRotation


# A dictionary to store registered users' data (in memory, not persistent)
registered_users: dict[str, User] = {}
manager = Manager()


def gen_pub_priv():
    private_key = RSA.generate(2048, get_random_bytes)
    public_key = private_key.publickey()
    return private_key, public_key


def add_user_to_register(username: str, number, pub):
    user = User(username, number, pub)
    registered_users[username.lower()] = user


def remove_user_from_register(username: str):
    registered_users.pop(username.lower())


# @app.route('/register', methods=['POST', 'GET'])
# def register():
#
#     data = {}
#     try:
#         if request.method == 'GET':
#             data = request.args
#             for k, v in data.items():
#                 print(f"{k}: {v}")
#         else:
#             data = request.json
#             for k, v in data.items():
#                 print(f"{k}: {v}")
#
#     except:
#         print("triple fail")
#
#     if 'username' not in data.keys() or 'number' not in data.keys():
#         return jsonify({'error': 'Missing username or number parameter'}), 400
#
#     username = data['username']
#     number = int(data['number'])
#
#     # Checking if the number is within the specified range
#     if not (100_000_0000 <= number <= 999_999_9999):
#         return jsonify({'error': 'Number should be between 1000000000 and 9999999999'}), 400
#     if username in registered_users.keys():
#         if registered_users[username]['number'] == number:
#             remove_user_from_register(username)
#     prkey, pubkey = gen_pub_priv()
#     add_user_to_register(username, number, pubkey)
#     return jsonify({'private_key': prkey.export_key().decode('utf-8')}), 200

@app.route('/register', methods=['POST'])
def register():
    return render_template('register.html')
@socketio.on('register')
def register(data):
    print(data)
    username = data['username']
    number = data['number']
    prkey, pubkey = gen_pub_priv()
    add_user_to_register(username, number, pubkey)
    send({'private_key': prkey.export_key().decode('utf-8')}, json=True)

@app.route('/listusers', methods=['GET'])
def list_users():
    ret = ""
    for username, user_obj in registered_users.items():
        user_name = user_obj.name
        user_number = user_obj.number

        ret += f"Username: {user_name}, Number: {user_number}\n"
    return ret, 200


@app.route('/set_open_to_play', methods=['POST'])
def set_open_to_play():
    data = request.json
    print(data)

    # Validate input
    if 'username' not in data or 'open_to_play' not in data:
        return jsonify({'error': 'Missing username or open_to_play parameter'}), 400

    username = data['username'].lower()
    open_to_play = data['open_to_play'].lower() in ['true', '1', 't', 'y', 'yes']

    # Update user status
    if username in registered_users:
        # Assuming you have a way to update the open_to_play status in your user object
        registered_users[username].open_to_play = open_to_play
        print(len(registered_users))
        msg = manager.create_games_for_open_players(registered_users)
        return jsonify({'message': f"{msg}"}), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/hostgame', methods=["POST", "GET"])
def host_game():
    if request.method == 'GET':
        print("GET")
    else:
        data = request.json
        print(data)
        if 'username' not in data:
            return jsonify({'error': 'Missing username, room_name, or capacity parameter'}), 400
        username = data['username'].lower()
        if username in registered_users:
            # Assuming you have a way to create a room and add it to your manager
            room = Room()
            manager.add_room(room)
            manager.add_user_to_room(registered_users[username], room.id)
            return jsonify({
                'message': f"User {username} has created a room {room.name} and room id {room.id}",
                'room_id': room.id
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404


@app.route("/<room_id>/join", methods=["POST"])
def join_game(room_id):
    data = request.json
    if 'username' not in data:
        return jsonify({'error': 'Missing username parameter'}), 400
    username = data['username'].lower()
    if username in registered_users:
        # Assuming you have a way to add a user to a room in your manager
        manager.add_user_to_room(registered_users[username], room_id)
        return jsonify({'message': f"User {username} has joined room {room_id}"}), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route("/<room_id>/leave", methods=["POST"])
def leave_game(room_id):
    data = request.json
    if 'username' not in data:
        return jsonify({'error': 'Missing username parameter'}), 400
    username = data['username'].lower()
    if username in registered_users:
        # Assuming you have a way to remove a user from a room in your manager
        manager.remove_user_from_room(registered_users[username], room_id)
        return jsonify({'message': f"User {username} has left room {room_id}"}), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route("/<room_id>/users", methods=["GET"])
def get_users_in_room(room_id):
    room = manager.get_room(room_id)
    if room:
        users = room.get_users()
        return jsonify({'users': [user.name for user in users]}), 200
    else:
        return jsonify({'error': 'Room not found'}), 404


@app.route("/<room_id>/set_ships", methods=["POST"])
def set_ships(room_id):
    data = request.json
    if 'username' not in data or 'ships' not in data:
        return jsonify({'error': 'Missing username or ships parameter'}), 400
    username = data['username'].lower()

    # Mapping of ship names to their sizes (as integers)
    ship_name_to_size = {
        "CARRIER": 5,
        "BATTLESHIP": 4,
        "SUBMARINE": 3,
        "DESTROYER": 2
    }
    # Convert the ship names to integers and the rotation strings to ShipRotation enums
    converted_ships = {}
    rotation_mapping = {
        "UP": ShipRotation.UP,
        "DOWN": ShipRotation.DOWN,
        "LEFT": ShipRotation.LEFT,
        "RIGHT": ShipRotation.RIGHT
    }

    for name, positions in data["ships"].items():
        size = ship_name_to_size[name]
        converted_positions = []
        for pos in positions:
            # Convert the rotation string to the corresponding ShipRotation enum value
            rotation_enum = rotation_mapping[pos["rotation"]]
            pos["rotation"] = rotation_enum
            converted_positions.append(pos)
        converted_ships[size] = converted_positions

    if username in registered_users:
        # Assuming you have a way to set ships for a user in a room in your manager
        manager.get_room(room_id).set_ships(registered_users[username], converted_ships)
        return jsonify({'message': f"room {room_id}: User {username} set ships {converted_ships}"}), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route("/<room_id>/get_status", methods=["GET"])
def get_status(room_id):
    room = manager.get_room(room_id)
    if room:
        status = room.battleship.get_status()
        status
        return jsonify({'status': status}), 200
    else:
        return jsonify({'error': 'Room not found'}), 404

@app.route("/rooms", methods=["GET"])
def list_rooms():
    ret = ""
    for room in manager.rooms:
        ret += f"Room ID: {room.id}, Users: {[user.name for user in room.get_users()]}\n"
    return jsonify({"message": ret}), 200

@app.route("/<room_id>/attack", methods=["POST"])
def attack(room_id):
    data = request.json
    if 'username' not in data or 'x' not in data or 'y' not in data:
        return jsonify({'error': 'Missing username, x, or y parameter'}), 400
    username = data['username'].lower()
    x = data['x']
    y = data['y']
    if username in registered_users:
        # Assuming you have a way to attack a user in a room in your manager
        result = manager.get_room(room_id).attack(registered_users[username].name, x, y)
        return jsonify({'message': f"room {room_id}: User {username} attacked {x}, {y} and {result}"}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    socketio.run(app, port=9999)
